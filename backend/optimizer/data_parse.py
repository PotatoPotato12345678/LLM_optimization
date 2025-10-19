import pandas as pd
import numpy as np
import requests

from llmModule.ED_views import ED_generate
from llmModule.EE_views import EE_generate

from io import BytesIO
import logging
logger = logging.getLogger(__name__)
BASE_URL = "http://localhost:8001"
def extract_A(data):
    # df_av = pd.read_json("mats/availability_mat_new.json")
    df_av = pd.DataFrame(data)
    df_av.drop("content", inplace=True)
    records = []

    for employee in df_av.columns:
        emp_data = df_av.iloc[0][employee]
        for date, shifts in emp_data.items():
            records.append({
                "employee": employee,
                "date": date,
                "shifts": shifts
            })

    df_flat_av = pd.DataFrame(records)
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
    
    df_flat_av2["availability"] = np.where(
        df_flat_av2["availability"] == "O",
        1,
        0
    )

    M_A = df_flat_av2[["employee", "date", "shift", "availability"]].values.tolist()

    return M_A

def extract_ED(data):
    # df_wi_mult = pd.read_json("mats/willingness_mat_new.json")  # substitute this with actual logic
    tmp = data.copy()
    data = {}
    for k, v in tmp.items():
       files = {
           'content': ('input.txt', BytesIO(v['content'].encode('utf-8')), 'text/plain')
       }
       data_tam = {
           'which_matrix': 'ed',
           'year': 2025,
           'month': 11,
           'metadata': 'ed_matrix'
       }
       response = requests.post(f"{BASE_URL}/get_matrix", files=files, data=data_tam)
       data[k] = response.json()
    df_wi_mult = pd.DataFrame(data)

    logger.info(data)
    rows = []
    records = []

    for day, rows in df_wi_mult.iterrows():
        for employee, shifts in rows.items():
            for s in shifts:
                logger.info(s)
                records.append({
                    "employee": employee,
                    "day": day,
                    "shift": s["shift"],
                    "willingness": s["willingness"]
                })
    df_wi_flat = pd.DataFrame(records)
    df_wi_flat["day"] = df_wi_flat["day"].str.extract(r"(\d+)").astype(int)
    df_wi_sorted = df_wi_flat.sort_values(by=["employee", "day", "shift"]).reset_index(drop=True)
    M_LLM_ED = df_wi_sorted[["employee", "day", "shift", "willingness"]].values.tolist()

    return M_LLM_ED

def extract_EE(data):
    tmp = data.copy()
    data = {}
    for k, v in tmp.items():
        logger.info(v)
        data[k] = ED_generate(v['content'])

    df_ee = pd.DataFrame(data)     # substitute with actual logic
    M_LLM_EE = []

    for row_name, row in df_ee.iterrows():
        for col_name, value in row.items():
            M_LLM_EE.append([row_name.upper(), col_name.upper(), float(value)])
    
    return M_LLM_EE