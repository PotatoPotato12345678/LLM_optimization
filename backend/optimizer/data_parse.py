import pandas as pd
import numpy as np
import requests
import time
import json
from io import BytesIO
import logging
from django.conf import settings
import os

logger = logging.getLogger(__name__)
BASE_URL = "http://host.docker.internal:8001"

def get_api_result(task_id, timeout=300):
    """Polls the status endpoint until the task is complete."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            url = f"{BASE_URL}/status/{task_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "done":
                logger.info(f"Task {task_id} is DONE.")
                return data["result"]
            elif data["status"] == "error":
                logger.error(f"Task {task_id} failed with error: {data.get('detail')}")
                return None
            
            logger.debug(f"Task {task_id} is {data['status']}. Waiting 2 seconds...")
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred while polling for task {task_id}: {e}")
            return None
    
    logger.error(f"Task {task_id} timed out after {timeout} seconds")
    return None

def extract_A(data):
    """Extract availability matrix from calendar data."""
    logger.info("Running extract_A")
    df_av = pd.DataFrame(data)
    records = []

    for employee in df_av.columns:
        emp_data = df_av.loc['availability_calendar'][employee]
        for date, shifts in emp_data.items():
            records.append({
                "employee": employee,
                "date": date,
                "shifts": shifts
            })

    df_flat_av = pd.DataFrame(records)
    if df_flat_av.empty:
        return []

    temp_record = []
    for _, row in df_flat_av.iterrows():
        for shift_name, availability in row["shifts"].items():
            temp_record.append({
                "employee": row["employee"],
                "date": row["date"],
                "shift": shift_name,
                "availability": availability
            })
    
    df_flat_av2 = pd.DataFrame(temp_record)
    df_flat_av2["availability"] = np.where(df_flat_av2["availability"] == "O", 1, 0)
    M_A = df_flat_av2[["employee", "date", "shift", "availability"]].values.tolist()
    logger.info(f"extract_A completed: {len(M_A)} rows")
    return M_A

def extract_ED(data, employee_list: list = None):
    """FIXED: Returns matrix with employee column included."""
    logger.info("Running extract_ED")
    
    all_content = "\n".join(v['content'] for v in data.values() if v.get('content'))
    if not all_content.strip():
        all_content = "特に希望なし"

    files = {'content': ('input.txt', BytesIO(all_content.encode('utf-8')), 'text/plain')}
    form_data = {'which_matrix': 'ed', 'year': 2025, 'month': 11}
    
    try:
        response = requests.post(f"{BASE_URL}/get_matrix", files=files, data=form_data, timeout=30)
        response.raise_for_status()
        task_id = response.json().get("task_id")
        
        if not task_id:
            logger.error("Failed to get task_id from server.")
            return []

        result = get_api_result(task_id)
        if result is None:
            return []

        df_wi_mult = pd.DataFrame(result)
        records = []
        for day, shifts in df_wi_mult.items():
            if isinstance(shifts, list):
                for s in shifts:
                    records.append({
                        "day": day,
                        "shift": s.get("shift"),
                        "willingness": s.get("willingness")
                    })

        if not records:
            return []
        
        df_wi_flat = pd.DataFrame(records)
        df_wi_flat["day"] = df_wi_flat["day"].str.extract(r"(\d+)").astype(int)
        df_wi_sorted = df_wi_flat.sort_values(by=["day", "shift"]).reset_index(drop=True)
        
        # FIXED: Add employee column - format [employee, day, shift, willingness]
        M_LLM_ED = []
        for employee in employee_list:
            for _, row in df_wi_sorted.iterrows():
                M_LLM_ED.append([employee, row["day"], row["shift"], row["willingness"]])

        logger.info(f"extract_ED completed: {len(M_LLM_ED)} rows")
        return M_LLM_ED

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to process ED matrix: {e}")
        return []

def extract_EE(data, employee_list: list):
    """FIXED: Returns proper employee-to-employee matrix."""
    logger.info("Running extract_EE")
    
    all_content = "\n".join(v['content'] for v in data.values() if v.get('content'))
    if not all_content.strip():
        all_content = "特に希望なし"

    files = {'content': ('input.txt', BytesIO(all_content.encode('utf-8')), 'text/plain')}
    form_data = {'which_matrix': 'ee', 'employees': json.dumps(employee_list)}
    
    try:
        response = requests.post(f"{BASE_URL}/get_matrix", files=files, data=form_data, timeout=30)
        response.raise_for_status()
        task_id = response.json().get("task_id")

        if not task_id:
            logger.error("Failed to get task_id from server.")
            return []

        result = get_api_result(task_id)
        if result is None:
            return []

        # FIXED: Create proper employee-to-employee pairs [employee1, employee2, willingness]
        M_LLM_EE = []
        
        if isinstance(result, dict):
            for emp1 in employee_list:
                for emp2 in employee_list:
                    willingness = result.get(emp1, {}).get(emp2, 0.0)
                    M_LLM_EE.append([emp1, emp2, float(willingness)])
        else:
            logger.warning("Unexpected result format from EE API, using default values")
            for emp1 in employee_list:
                for emp2 in employee_list:
                    willingness = 1.0 if emp1 == emp2 else 0.5
                    M_LLM_EE.append([emp1, emp2, willingness])

        logger.info(f"extract_EE completed: {len(M_LLM_EE)} rows")
        return M_LLM_EE

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to process EE matrix: {e}")
        return []


def generate_data_json(availability_data, preference_data, employee_list, 
                       num_shifts=2, num_days=30, time_open=9, time_close=18):
    """
    Main function to generate complete data.json file for Django views/management commands.
    
    Args:
        availability_data: Calendar availability data for extract_A
        preference_data: Preference text data for extract_ED and extract_EE
        employee_list: List of employee names/IDs
        num_shifts: Number of shifts per day (default: 2)
        num_days: Number of days in schedule (default: 30)
        time_open: Opening hour (default: 9)
        time_close: Closing hour (default: 18)
    
    Returns:
        dict: Complete data dictionary that was written to data.json
    """
    logger.info("Starting data.json generation...")
    
    # Extract all matrices
    M_A = extract_A(availability_data)
    M_LLM_ED = extract_ED(preference_data)
    M_LLM_EE = extract_EE(preference_data, employee_list)
    
    # Prepare complete data structure
    data = {
        "E": employee_list,
        "n": len(employee_list),
        "S": num_shifts,
        "m": num_days,
        "time_open": time_open,
        "time_close": time_close,
        "M_A": M_A,
        "M_LLM_ED": M_LLM_ED,
        "M_LLM_EE": M_LLM_EE
    }
    
    # Determine output path (use BASE_DIR if available, otherwise current directory)
    try:
        base_dir = settings.BASE_DIR
        output_path = os.path.join(base_dir, 'data.json')
    except:
        output_path = 'data.json'
    
    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Successfully wrote data to {output_path}")
    logger.info(f"Employees: {len(employee_list)}, M_A: {len(M_A)}, "
                f"M_LLM_ED: {len(M_LLM_ED)}, M_LLM_EE: {len(M_LLM_EE)}")
    
    return data