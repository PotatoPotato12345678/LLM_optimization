import pandas as pd

def gen_availability():
    pass

def gen_willingness():
    df_will = pd.read_json('mats/willingness_mat.json')   # substitute this with actual logic

    rows = []
    for day, row in df_will.iterrows():
        for employee, shifts in row.items():
            for s in shifts:
                rows.append({
                    "employee": employee,
                    "day": day,
                    "shift": s["shift"],
                    "willingness": s["willingness"]
                })

    df_flat = pd.DataFrame(rows)
    df_flat["day"] = df_flat["day"].str.extract(r"(\d+)").astype(int)
    shift_order = pd.CategoricalDtype(categories=["morning", "evening"], ordered=True)
    df_flat["shift"] = df_flat["shift"].map({0: "morning", 1: "evening"}).astype(shift_order)
    df_sorted = df_flat.sort_values(["employee", "day", "shift"]).reset_index(drop=True)

    M_LLM_willingness = df_sorted[["employee", "day", "shift", "willingness"]].values.tolist()

    return M_LLM_willingness

if __name__ == "__main__":
    M_LLM_willingness = gen_willingness()
    for row in M_LLM_willingness:
        print(rows)