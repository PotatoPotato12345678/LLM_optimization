# Introduction - Problem Definition
- For managers at stores with a lat of employees, they should make shift schedule for every month.
- Followings are the fators which make this process challenging
	1. The number of employee is always changing
	2. Everyone has different preference
	3. Employees' preferences are also simultaneously changing
	4. Manager should respect employees' preference as much as possible
- Because the manager should respect employee's preference and availability as much as possible, considering all of them makes the job extremely time-consuming.
- Also, this job should be done every month, this lowers manager's efficiency
- Automate this job can enhance manager's efficiency and makes the job less expensive.

# Methodology
![[system_diagram.jpg]]
## Overview

| Module        | Technology stack                                  | Description                                                                                                        |
| ------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Frontend      | React(JavaScript)<br>Django(Python)<br>PostgreSQL | Managers / Employee can enter their preference and availability using UI and natural language                      |
| LLM Extractor | Python<br>OpenAI API                              | LLM will convert preference written in natural language into matrices                                              |
| Optimizer     | Python<br>Pyomo<br>IPOPT (Solver)                 | Optimizer will generate optimized shift using information given by LLM Extractor                                   |
| LLM Extractor | Python<br>OpenAI API                              | More than one shifts will be generated from optimizer. This module evaluates all of them and chooses the best one. |


## Frontend
![[frontend.png]]
Used **React(JavaScript)**, **Django(Python)** and **PostgreSQL** for implementation
- **Synergy**: People can explain with whom they want to work with using natural language
- **Availability**: People can input their availability in calendar

This information will be passed to LLM extractor.
## LLM Extractor
Used **Python**, **OpenAI API** and **fine-tuned** to fit the purpose
This module gets *Availability* and *Synergy* information as input and generates matrices for next module
- **ED-Matrix**: This matrix represents Availability between *Employee*, *Days*, and *Shifts*
	- 3rd dimensional matrix
- **EE-Matrix**: This matrix represents synergy between *Employee* and another *Employee*
	- 2nd dimensional matrix
## Optimizer
Used **Python** and **Pyomo** (Python package for solving mathematical optimization problem)
- This module is mathematical optimizer to solve optimization problem
- Implemented mathematical expression and function and solve the problem
### Primary Variables
![Primary Variables](https://latex.codecogs.com/svg.image?\begin{aligned}\text{Employee}:\quad&E=\{e_1,e_2,\ldots,e_i\}&\quad\text{Employee}\\[6pt]\text{Days}:\quad&D=\{d_1,d_2,\ldots,d_j\}&\quad\text{Days&space;in&space;Month}\\[6pt]\text{Shifts}:\quad&S=\{s_1,s_2,\dots,s_k\}&\quad\text{Shifts&space;in&space;a&space;day}\\[6pt]\end{aligned})
- These variables are primary variables
- Primary variables are used to defining the problem
### Supplementary Variables
![Supplementary Variables](https://latex.codecogs.com/png.latex?%5Cbegin%7Barray%7D%7Clcl%7C%0A%5Ctext%7BEmployee%7D%3A%26E%3D%5C%7Be_1%2Ce_2%2C%5Cldots%2Ce_i%5C%7D%26%5Ctext%7BEmployee%7D%5C%5C%0A%5Ctext%7BDays%7D%3A%26D%3D%5C%7Bd_1%2Cd_2%2C%5Cldots%2Cd_j%5C%7D%26%5Ctext%7BDays%20in%20Month%7D%5C%5C%0A%5Ctext%7BShifts%7D%3A%26S%3D%5C%7Bs_1%2Cs_2%2C%5Cdots%2Cs_k%5C%7D%26%5Ctext%7BShifts%20in%20a%20day%7D%0A%5Cend%7Barray%7D)

- These variables are used to explain **Primary Variables**
### Primary Variables (Matrices)
![Primary Variables (Matrix)](https://latex.codecogs.com/svg.image?\begin{aligned}\text{Employee-Day&space;Matrix}:\quad&M_{LLM,E,D,S}\in\mathbb{R}^{E\times&space;D\times&space;S}\quad&\text{(LLM&space;output)}\\[6pt]\text{Employee-Employee&space;Matrix}:\quad&M_{LLM,E,D,S}\in\mathbb{R}^{E\times&space;E'}\quad&\text{(LLM&space;output)}\\[6pt]\text{Assignment&space;Matrix}:\quad&A_{E,D,S}\in\mathbb{R}^{E\times&space;D\times&space;S}\quad&\text{Shift&space;assignments}\\[6pt]&\quad\quad\quad\left\{\begin{array}{ll}1&\text{if&space;assigned}\\0&\text{otherwise}\end{array}\right.\quad\text{for}E\times&space;D\times&space;S\\[6pt]\end{aligned})
### Decision Variables
![Decision Variables](https://latex.codecogs.com/svg.image?\begin{aligned}\text{Employee-Day&space;Matrix}:\quad&M_{sugg,E,D,S}\in\mathbb{R}^{E\times&space;D\times&space;S}\quad&\text{(Optimized&space;output)}\\[6pt]\text{Employee-Employee&space;Matrix}:\quad&M_{sugg,E,E'}\in\mathbb{R}^{E\times&space;E'}\quad&\text{(Optimized&space;output)}\\[6pt]\end{aligned})
- **Decision Variables** are matrices that would be generated as a result
- These would be the solution of provided problem
### Constraints
![Constrains](https://latex.codecogs.com/svg.image?\begin{aligned}\forall&space;d\in&space;D,\;\forall&space;s\in&space;S,\quad&\sum_{e\in&space;E}A_{\text{E,D,S}}(e,d,s)=2&\text{for&space;each&space;shift,exact&space;two&space;employees&space;work}\\[6pt]\forall&space;e\in&space;E,\quad&\sum_{d\in&space;D}\sum_{s\in&space;S}A_{\text{E,D,S}}(e,d,s)>0&\text{Each&space;employee&space;has&space;to&space;work&space;once&space;a&space;week&space;at&space;least}\\[6pt]\forall&space;e\in&space;E,\quad&\sum_{d\in&space;D}\sum_{s\in&space;S}A_{\text{E,D,S}}(e,d,s)\times&space;H_{shift}\le&space;40&\text{Each&space;employee&space;cannot&space;work&space;more&space;than&space;40&space;hours&space;per&space;week}\\[6pt]\forall&space;e\in&space;E,\forall&space;d\in&space;D,\quad&\sum_{s\in&space;S}A_{\text{E,D,S}}(e,d,s)\times&space;H_{shift}\le&space;8&\text{Each&space;employee&space;cannot&space;work&space;more&space;than&space;8&space;hours&space;in&space;a&space;day}\end{aligned})
- **Constraints** are the rules the optimizer should obey
- Generated shift should fulfill every constraint
### Objective Function
**ED Loss**
![ED Loss](https://latex.codecogs.com/svg.image?&space;EDLoss=\alpha(\frac{1}{|E|\times|D|\times|S|}\sum_{e\in&space;E}\sum_{d\in&space;D}\sum_{s\in&space;S}|M_{LLM,e,d,s}-M_{sugg,e,d,s}|)&plus;\beta(\sum_{e\in&space;E}\frac{M_{LLM,e,D,S}\cdot{M_{sugg,e,D,S}}}{||M_{LLM,e,D,S||}\cdot||M_{sugg,e,D,S||}})&plus;\gamma(\frac{M_{LLM,e,D,S}\cdot{M_{sugg,e,D,S}}}{||M_{LLM,E,D,S||}\cdot||M_{sugg,E,D,S||}}))
EDLoss calculates:
	1. Element-wise difference between $M_{LLM, E, D, S}$ and $M_{sugg, E, D, S}$ add all the values and gets mean
	2. Employee-wise cosine similarity between  $M_{LLM, E, D, S}$ and $M_{sugg, E, D, S}$
	3. Cosine similarity between  $M_{LLM, E, D, S}$ and $M_{sugg, E, D, S}$
And gets summation of all of terms calculated above

**EE Loss**
![EE Loss](https://latex.codecogs.com/svg.image?&space;EELoss=\alpha(\frac{1}{|E|^2}\sum_{e\in&space;E}\sum_{e'\in&space;E}|M_{LLM,e,e'}-M_{sugg,e,e'}|)&plus;\beta(\sum_{e\in&space;E}\frac{M_{LLM,e,E}\cdot{M_{sugg,e,E}}}{||M_{LLM,e,E||}\cdot||M_{sugg,e,E||}})&plus;\gamma(\frac{M_{LLM,E,E'}\cdot{M_{sugg,E,E'}}}{||M_{LLM,E,E'||}\cdot||M_{sugg,E,E'||}}))
EELoss calculates:
	1. Element-wise difference between $M_{LLM, E, E'}$ and $M_{sugg, E, E'}$ add all the values and gets mean
	2. Employee-wise cosine similarity between  $M_{LLM, E, E'}$ and $M_{sugg, E, E'}$
	3. Cosine similarity between  $M_{LLM, E, E'}$ and $M_{sugg, E, E'}$
And gets summation of all of terms calculated above

$\alpha$, $\beta$, $\gamma$ are weights which will be applied to each element of $EDLoss$ and $EELoss$
Coefficients are fixed as one by default

**Integrated Function**
![Integrated Function](https://latex.codecogs.com/svg.image?&space;Obj=Z_1\cdot&space;EDLoss&plus;Z_2\cdot&space;EELoss)
- Objective function calculates total loss value of $EDLoss$ and $EELoss$
- $Z_1$ and $Z_2$ are weights which will be applied to $EDLoss$ and $EELoss$
	- Coefficients are fixed as one by default

**Objective**
![Objective function](https://latex.codecogs.com/svg.image?\begin{aligned}\min_{\substack{M_{\text{sugg},E,D,S},\;M_{\text{sugg},E,E'}\;}}&\text{Obj}\bigl(EDLoss,\;EELoss\bigr)\end{aligned})
The objective of this problem is:
- Find $M_{\text{sugg}, E, D, S}$ and $M_{\text{sugg}, E, E'}$ which minimize the $EDLoss$ and $EELoss$
- which follows all the pre-set constraints
## LLM Evaluator
- **Optimizer** generates multiple shift with multiple coefficients.
- **Evaluator** will evaluate all of them and choose the best one
# Discussion - Why We Chose This Structure?
## Why Not Machine Learning?
- Applying machine learning is ***possible*** but, there are some problems
- We did not have enough data to train the model
- Model may be settle in local optima while fitting
- It is computationally expensive, which is not applicable for project like this (which requires real time calculation)
## Why Not Purely LLM?
- LLMs are good at classifying given data into different categories
- But, LLMs have possibility to generate hallucinated results which is not intended output
	- This output can be *partially optimized solution* or ***not applicable at all***
- Lastly, there is a **blackbox problem**
	- We don't know what is going on inside LLMs which makes process opaque
	- For project like this, every information should be as transparent as possible
## Why We Combined LLMs And Optimization?
### LLMs
- As mentioned above, LLMs are good at classifying and can process natural language
- Therefore, LLMs can extract preferences from natural language and convert them into numbers
- When *fine-tuned* properly, hallucination can be minimized
### Mathematical Optimization
- Unlike LLMs or machine learning methods, mathematical optimization methods derives solution analytically
- This solution derived with these solvers are already proved that those are the best solutions for this.
- Therefore, we can ensure our solution is the best solution
- In case of open-sourced solvers, their algorithm is opened to public and everyone can check their algorithms
	- Therefore, the process is transparent and everyone can understand what is going on inside the box
# Limitations
- We are still relying on LLMs, and our solution still can be non-optimal solution
- We don't know how our **Evaluator** evaluates outputs, and choose best one **(Blackbox problem)**
- The coefficients we applied on our objective function are fixed
# Future Work
## Methodology
![[system_diagram.jpg]]
- Apply *Simulated Annealing (SA) method* or other metaheuristic method for hyper-parameter tuning
	- **Hyper-parameter tuning**: finding best coefficients for our model
	- This will substitute our **Evaluator** module
	- This will mitigate the **Blackbox problem**
- Apply iterative evaluation
	- After evaluate the output, **back-propagate** found hyper-parameters to optimizer and evaluate again
	- Iteration will be finished when it fulfills certain criteria or after it ran certain numbers of iterations
	- This will enhance the performance
- Apply XAIs (eXplainable AIs) for extracting preferences
	- This will mitigate the **Blackbox problem**
## Functionalities
- Employee can include secret requirements
	- This will be invisible for managers
	- This can include 1) the person who don't want to work with, 2) private information
- Dynamic constraints
	- Currently, constraints (pre-set rules) are fixed and cannot be changed
- Handles the situation where no feasible area exists by compromising constraints
	- Then inform managers about it after the process done
- Managers can edit the optimized shifts on an interactive UI
- Managers can edit user database
- The system can handle the information about which employees belong to which managers.
	- Currently, managers handle all the employee’s in database.
# Executing
- You need [Docker](https://www.docker.com/) and [Git](https://git-scm.com/downloads) to run the program
- Pull the repository by running following command in terminal
```bash
git clone git@github.com:PotatoPotato12345678/LLM_optimization.git
```
- Direct to the project directory in terminal
- Run following command in terminal
```bash
docker-compose up --build --remove-orphans
```
- Web server will start from:
```http
http://localhost:3000/
```
- Access to the address via web browser
- Enjoy!
# Authors
- **Ikuta** Toma
- **Lin** Chung-Hsi
- Tamjidur MD **Rahman**
- **Kim** Wonil
