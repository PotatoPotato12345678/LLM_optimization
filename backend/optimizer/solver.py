import pyomo.environ as pyo
from .model_def import model as m
import json
import os


def solver():
    # define solver
    solver = "cbc"
    SOLVER = pyo.SolverFactory(solver)

    if not SOLVER.available():
        raise RuntimeError(f"Solver {solver} is not available.")

    # Load data from JSON file (allow running from project root or package dir)
    data_file = os.environ.get('PYOMO_DATA_FILE', 'data.json')
    if not os.path.isabs(data_file):
        # try backend/optimizer relative path
        candidate = os.path.join(os.getcwd(), 'backend', 'optimizer', data_file)
        if os.path.exists(candidate):
            data_file = candidate

    with open(data_file, 'r') as f:
        data = json.load(f)

    # Create a Pyomo data dictionary
    pyomo_data = {None: {
        'E': {None: data.get('E', [])},
        # 'S': {None: data['S']},
        'n': {None: data.get('n', 0)},
        'm': {None: data.get('m', 2)},
        'time_open': {None: data.get('time_open', 9)},
        'time_close': {None: data.get('time_close', 17)},
        'M_LLM_ED': {tuple(item[:3]): item[3] for item in data.get('M_LLM_ED', [])},
        'M_LLM_EE': {tuple(item[:2]): item[2] for item in data.get('M_LLM_EE', [])}
    }}

    # Create a model instance
    instance = m.create_instance(pyomo_data)

    # Solve the model
    results = SOLVER.solve(instance, tee=True)

    # Print the results
    print(results)

    # Print the value of the objective function
    print(f"Objective function value: {pyo.value(instance.minimize_oss)}")

    # Print the values of the variables
    print("A (Assignment Matrix):")
    for (e, d, s), val in instance.A.items():
        if pyo.value(val) > 0:
            print(f"  {e}, {d}, {s}: {pyo.value(val)}")

    print("M_sugg_EE (Suggested Employee-Employee Matrix):")
    for (e1, e2), val in instance.M_sugg_EE.items():
        print(f"  {e1}, {e2}: {pyo.value(val)}")
import pyomo.environ as pyo
from .model_def import model as m
import json
import os


def solver():
    # define solver
    solver = "cbc"
    SOLVER = pyo.SolverFactory(solver)

    if not SOLVER.available():
        raise RuntimeError(f"Solver {solver} is not available.")

    # Load data from JSON file (allow running from project root or package dir)
    data_file = os.environ.get('PYOMO_DATA_FILE', 'data.json')
    if not os.path.isabs(data_file):
        # try backend/optimizer relative path
        candidate = os.path.join(os.getcwd(), 'backend', 'optimizer', data_file)
        if os.path.exists(candidate):
            data_file = candidate

    with open(data_file, 'r') as f:
        data = json.load(f)

    # Create a Pyomo data dictionary
    pyomo_data = {None: {
        'E': {None: data.get('E', [])},
        # 'S': {None: data['S']},
        'n': {None: data.get('n', 0)},
        'm': {None: data.get('m', 2)},
        'time_open': {None: data.get('time_open', 9)},
        'time_close': {None: data.get('time_close', 17)},
        'M_LLM_ED': {tuple(item[:3]): item[3] for item in data.get('M_LLM_ED', [])},
        'M_LLM_EE': {tuple(item[:2]): item[2] for item in data.get('M_LLM_EE', [])}
    }}

    # Create a model instance
    instance = m.create_instance(pyomo_data)

    # Solve the model
    results = SOLVER.solve(instance, tee=True)

    # Print the results
    print(results)

    # Print the value of the objective function
    print(f"Objective function value: {pyo.value(instance.minimize_oss)}")

    # Print the values of the variables
    print("A (Assignment Matrix):")
    for (e, d, s), val in instance.A.items():
        if pyo.value(val) > 0:
            print(f"  {e}, {d}, {s}: {pyo.value(val)}")

    print("M_sugg_EE (Suggested Employee-Employee Matrix):")
    for (e1, e2), val in instance.M_sugg_EE.items():
        print(f"  {e1}, {e2}: {pyo.value(val)}")
