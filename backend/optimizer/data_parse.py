import pandas as pd
import numpy as np
import json


def _to_dataframe(maybe_json):
    """Try to convert input to a pandas DataFrame.

    Accepts a JSON string, a dict, or a DataFrame and returns a DataFrame.
    """
    if isinstance(maybe_json, pd.DataFrame):
        return maybe_json
    if isinstance(maybe_json, str):
        try:
            return pd.read_json(maybe_json)
        except Exception:
            try:
                return pd.read_json(json.dumps(json.loads(maybe_json)))
            except Exception:
                raise
    if isinstance(maybe_json, dict):
        # Try to construct DataFrame directly; keys -> columns
        try:
            return pd.DataFrame(maybe_json)
        except Exception:
            # Last resort: convert dict to JSON then read
            return pd.read_json(json.dumps(maybe_json))


def extract_A(data):
    # If input is a plain dict mapping employee -> {date: {shift: availability}}
    records = []
    if isinstance(data, dict):
        try:
            for employee, emp_data in data.items():
                if not isinstance(emp_data, dict):
                    continue
                for date, shifts in emp_data.items():
                    records.append({
                        "employee": employee,
                        "date": date,
                        "shifts": shifts,
                    })
        except Exception as exc:
            print("extract_A: error iterating dict input:", exc)
            return []

    if not records:
        # fallback to DataFrame-based parsing
        try:
            df_av = _to_dataframe(data)
        except Exception as exc:
            print("extract_A: failed to parse data into DataFrame:", exc)
            return []

        # If 'content' is a column, drop it
        if "content" in df_av.columns:
            try:
                df_av = df_av.drop(columns=["content"])
            except Exception:
                pass

        try:
            for employee in df_av.columns:
                try:
                    emp_data = df_av.iloc[0][employee]
                except Exception:
                    emp_data = df_av[employee]
                if isinstance(emp_data, dict):
                    for date, shifts in emp_data.items():
                        records.append({
                            "employee": employee,
                            "date": date,
                            "shifts": shifts,
                        })
        except Exception as exc:
            print("extract_A: error while flattening records:", exc)
            return []

    if not records:
        return []

    df_flat_av = pd.DataFrame(records)
    temp_record = []
    for _, row in df_flat_av.iterrows():
        shifts = row.get("shifts") if isinstance(row, dict) else row["shifts"]
        if not isinstance(shifts, dict):
            continue
        for shift_name, availability in shifts.items():
            temp_record.append({
                "employee": row["employee"],
                "date": row["date"],
                "shift": shift_name,
                "availability": availability,
            })

    df_flat_av2 = pd.DataFrame(temp_record)
    if df_flat_av2.empty:
        return []

    df_flat_av2["availability"] = np.where(df_flat_av2["availability"] == "O", 1, 0)

    M_A = df_flat_av2[["employee", "date", "shift", "availability"]].values.tolist()
    return M_A

def extract_ED(data):
    try:
        df_wi_mult = _to_dataframe(data)
    except Exception as exc:
        print("extract_ED: failed to parse data:", exc)
        return []

    records = []
    try:
        for day, row in df_wi_mult.iterrows():
            # row is expected to be a mapping employee -> list of shifts
            for employee, shifts in row.items():
                if not isinstance(shifts, list):
                    continue
                for s in shifts:
                    # s expected to be dict with 'shift' and 'willingness'
                    if not isinstance(s, dict):
                        continue
                    records.append({
                        "employee": employee,
                        "day": day,
                        "shift": s.get("shift"),
                        "willingness": s.get("willingness"),
                    })
    except Exception as exc:
        print("extract_ED: error while iterating:", exc)
        return []

    if not records:
        return []

    df_wi_flat = pd.DataFrame(records)
    # try to extract numeric day if possible
    if "day" in df_wi_flat.columns and df_wi_flat["day"].dtype == object:
        try:
            df_wi_flat["day"] = df_wi_flat["day"].astype(str).str.extract(r"(\d+)")[0].astype(float).astype(int)
        except Exception:
            pass

    df_wi_sorted = df_wi_flat.sort_values(by=[col for col in ["employee", "day", "shift"] if col in df_wi_flat.columns]).reset_index(drop=True)
    M_LLM_ED = df_wi_sorted[[c for c in ["employee", "day", "shift", "willingness"] if c in df_wi_sorted.columns]].values.tolist()
    return M_LLM_ED

def extract_EE(data):
    try:
        df_ee = _to_dataframe(data)
    except Exception as exc:
        print("extract_EE: failed to parse data:", exc)
        return []

    M_LLM_EE = []
    try:
        for row_name, row in df_ee.iterrows():
            for col_name, value in row.items():
                try:
                    val = float(value)
                except Exception:
                    continue
                M_LLM_EE.append([str(row_name).upper(), str(col_name).upper(), val])
    except Exception as exc:
        print("extract_EE: error while iterating:", exc)
        return []

    return M_LLM_EE