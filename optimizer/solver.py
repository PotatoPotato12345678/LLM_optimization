import pyomo.environ as pyo
from model_def import model as m
import json

# define solver
solver = "appsi_highs"
SOLVER = pyo.SolverFactory(solver)

assert SOLVER.available(), f"Solver {solver} is not available."

# Load data from JSON file
with open('data.json', 'r') as f:
    data = json.load(f)

# Create a Pyomo data dictionary
pyomo_data = {None: {
    'E': {None: data['E']},
    'S': {None: data['S']},
    'n': {None: data['n']},
    'm': {None: data['m']},
    'time_open': {None: data['time_open']},
    'time_close': {None: data['time_close']},
    'M_LLM_ED': {tuple(item[:3]): item[3] for item in data['M_LLM_ED']},
    'M_LLM_EE': {tuple(item[:2]): item[2] for item in data['M_LLM_EE']}
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
