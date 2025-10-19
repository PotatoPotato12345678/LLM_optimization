from fastapi import FastAPI, Form, UploadFile, HTTPException
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import uuid
from typing import Dict, Any
import tiktoken
import calendar
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Tuple
import json
import os
# --- Global Setup ---
# Define Model
#Task: Move to env file later

model = os.getenv("MODEL_NAME", "gpt-5-nano-2025-08-07")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=api_key)

class ShiftItem(BaseModel):
    shift: int
    willingness: float
class Employee(BaseModel):
    id: str
    willingness: float
class EmployeeWillingness(BaseModel):
    employees: List[Employee]

# ThreadPool for background tasks
executor = ThreadPoolExecutor(max_workers=4)
# This will store the Future objects for our background tasks
tasks: Dict[str, asyncio.Future] = {}


# --- Helper Functions ---
def count_tokens(text: str, model: str = model) -> int:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    return len(tokens)
def month_days_with_weekdays(year: int, month: int):
    # Get number of days in the month
    _, num_days = calendar.monthrange(year, month)
    # Create a flat string with day followed by weekday abbreviation
    days_weekdays = "".join(
        f"{day}({calendar.day_abbr[calendar.weekday(year, month, day)]}) "
        for day in range(1, num_days + 1)
    ).strip()
    return days_weekdays, num_days

def ED_matrix(text_input: str, year: int , month: int) -> Dict[str, Any]:
    match month_days_with_weekdays(year, month)[1]:
            case 28:
                class ShiftWillingness28(BaseModel):
                    d1: List[ShiftItem]
                    d2: List[ShiftItem]
                    d3: List[ShiftItem]
                    d4: List[ShiftItem]
                    d5: List[ShiftItem]
                    d6: List[ShiftItem]
                    d7: List[ShiftItem]
                    d8: List[ShiftItem]
                    d9: List[ShiftItem]
                    d10: List[ShiftItem]
                    d11: List[ShiftItem]
                    d12: List[ShiftItem]
                    d13: List[ShiftItem]
                    d14: List[ShiftItem]
                    d15: List[ShiftItem]
                    d16: List[ShiftItem]
                    d17: List[ShiftItem]
                    d18: List[ShiftItem]
                    d19: List[ShiftItem]
                    d20: List[ShiftItem]
                    d21: List[ShiftItem]
                    d22: List[ShiftItem]
                    d23: List[ShiftItem]
                    d24: List[ShiftItem]
                    d25: List[ShiftItem]
                    d26: List[ShiftItem]
                    d27: List[ShiftItem]
                    d28: List[ShiftItem]
                ShiftWillingnessModel = ShiftWillingness28
            case 29:
                class ShiftWillingness29(BaseModel):
                    d1: List[ShiftItem]
                    d2: List[ShiftItem]
                    d3: List[ShiftItem]
                    d4: List[ShiftItem]
                    d5: List[ShiftItem]
                    d6: List[ShiftItem]
                    d7: List[ShiftItem]
                    d8: List[ShiftItem]
                    d9: List[ShiftItem]
                    d10: List[ShiftItem]
                    d11: List[ShiftItem]
                    d12: List[ShiftItem]
                    d13: List[ShiftItem]
                    d14: List[ShiftItem]
                    d15: List[ShiftItem]
                    d16: List[ShiftItem]
                    d17: List[ShiftItem]
                    d18: List[ShiftItem]
                    d19: List[ShiftItem]
                    d20: List[ShiftItem]
                    d21: List[ShiftItem]
                    d22: List[ShiftItem]
                    d23: List[ShiftItem]
                    d24: List[ShiftItem]
                    d25: List[ShiftItem]
                    d26: List[ShiftItem]
                    d27: List[ShiftItem]
                    d28: List[ShiftItem]
                    d29: List[ShiftItem]
                ShiftWillingnessModel = ShiftWillingness29
            case 30:
                class ShiftWillingness30(BaseModel):
                    d1: List[ShiftItem]
                    d2: List[ShiftItem]
                    d3: List[ShiftItem]
                    d4: List[ShiftItem]
                    d5: List[ShiftItem]
                    d6: List[ShiftItem]
                    d7: List[ShiftItem]
                    d8: List[ShiftItem]
                    d9: List[ShiftItem]
                    d10: List[ShiftItem]
                    d11: List[ShiftItem]
                    d12: List[ShiftItem]
                    d13: List[ShiftItem]
                    d14: List[ShiftItem]
                    d15: List[ShiftItem]
                    d16: List[ShiftItem]
                    d17: List[ShiftItem]
                    d18: List[ShiftItem]
                    d19: List[ShiftItem]
                    d20: List[ShiftItem]
                    d21: List[ShiftItem]
                    d22: List[ShiftItem]
                    d23: List[ShiftItem]
                    d24: List[ShiftItem]
                    d25: List[ShiftItem]
                    d26: List[ShiftItem]
                    d27: List[ShiftItem]
                    d28: List[ShiftItem]
                    d29: List[ShiftItem]
                    d30: List[ShiftItem]
                ShiftWillingnessModel = ShiftWillingness30
            case 31:
                class ShiftWillingness31(BaseModel):
                    d1: List[ShiftItem]
                    d2: List[ShiftItem]
                    d3: List[ShiftItem]
                    d4: List[ShiftItem]
                    d5: List[ShiftItem]
                    d6: List[ShiftItem]
                    d7: List[ShiftItem]
                    d8: List[ShiftItem]
                    d9: List[ShiftItem]
                    d10: List[ShiftItem]
                    d11: List[ShiftItem]
                    d12: List[ShiftItem]
                    d13: List[ShiftItem]
                    d14: List[ShiftItem]
                    d15: List[ShiftItem]
                    d16: List[ShiftItem]
                    d17: List[ShiftItem]
                    d18: List[ShiftItem]
                    d19: List[ShiftItem]
                    d20: List[ShiftItem]
                    d21: List[ShiftItem]
                    d22: List[ShiftItem]
                    d23: List[ShiftItem]
                    d24: List[ShiftItem]
                    d25: List[ShiftItem]
                    d26: List[ShiftItem]
                    d27: List[ShiftItem]
                    d28: List[ShiftItem]
                    d29: List[ShiftItem]
                    d30: List[ShiftItem]
                    d31: List[ShiftItem]
                ShiftWillingnessModel = ShiftWillingness31
    main_context = f"""
        This month has the following weekdays: {month_days_with_weekdays(year, month)[0]}

        Task:
        - Comprehend the given text input in Japanese and classify willingness to work each shift for every day of the month.

        Output Format:
        - JSON object with keys "d1" to "dN" (N = number of days in the month).
        - Each value is a list of [SHIFT, WILLINGNESS] pairs:
        - SHIFT 0 = Early shift
        - SHIFT 1 = Late shift
        - Example:
        {{
            "d1": [[0, -0.4], [1, -0.4]],
            "d2": [[0, 0.5], [1, 0.5]],
            "d5": [[0, 0.9], [1, 0.9]]
        }}

        Willingness Scale:
        - Very unwilling: -1.0 to -0.6 (exclusive)
        - Slightly unwilling: -0.6 to -0.2 (exclusive)
        - Neutral: -0.2 to 0.2 (exclusive)
        - Slightly willing: 0.2 to 0.6 (exclusive)
        - Very willing: 0.6 to 1.0 (inclusive)

        Japanese Phrase Mapping (with precedence rules):
        - If a phrase contains both positive and negative (e.g., "入れるけどできれば入りたくない"), **the negative overrides the positive**.
        - "入れる" or "働ける" → slightly willing (0.2–0.6)
        - "できれば入りたくない" → slightly unwilling (-0.6 to -0.2)
        - "無理" or "絶対無理" → very unwilling (-1.0 to -0.6)
        - "一番嬉しい" or "大好き" → very willing (0.6–1.0)

        Shift Mapping:
        - "早め" → assign the willingness only to Early shift (shift 0)
        - "遅め" → assign the willingness only to Late shift (shift 1)
        - If no time is mentioned, assign the same value to both shifts

        Instructions:
        1. Never hallucinate information; only use what is explicitly stated.
        2. Identify willingness at the phrase level in the input text.
        3. Resolve conflicts using the precedence rules above.
        4. Assign willingness to the correct day(s) mentioned.
        5. Days not mentioned in the text should default to neutral (0) for both shifts.
        6. Every day in the month must have a value for both shifts.
        7. Only return the JSON object; do not include any explanations or extra text.
        """
    response = client.responses.parse(
    model=model,
    input=[
        {"role": "system", "content": main_context},
        {"role": "user", "content": text_input},
    ],
    text_format=ShiftWillingnessModel,
    )
    # Extract just the parsed data instead of the entire response
    result = response.output_parsed
    print("________________________________")
    print(f"Input Text:{text_input} year:{year} month:{month}")
    print(response.model_dump)
    print("________________________________")
    print(result)
    print("________________________________")
    return result

def EE_matrix(text_input: str, employee_list: List[str]) -> Dict[str, Any]:
    employee_flat = ", ".join([f"e{i+1}:{name}" for i, name in enumerate(employee_list)])
    main_context_1 = f"""
    The available employees are: {employee_flat}. Total employees are {len(employee_list)}.
    Task:
    - Comprehend the given text input in Japanese and classify willingness to work with a given employee.

    Output Format:
    - JSON object with keys "e1" to "eN" (N = {len(employee_list)}).
    - The value indicates willingness to work with that employee.
    - Employees not mentioned in the text MUST default to neutral (0)."""
    main_context_2 = """
    - Example:
    {
    "employees": {
        "e1": float,
        "e2": float,
        "e3": float,
        ...
        "eN":float
    }
    }


    Willingness Scale:
    - Very unwilling: -1.0 to -0.6 (exclusive)
    - Slightly unwilling: -0.6 to -0.2 (exclusive)
    - Neutral: -0.2 to 0.2 (exclusive)
    - Slightly willing: 0.2 to 0.6 (exclusive)
    - Very willing: 0.6 to 1.0 (inclusive)

    Japanese Phrase Mapping (with precedence rules):
    - If a phrase contains both positive and negative (e.g., "入れるけどできれば入りたくない"), **the negative overrides the positive**.
    - "入れる" or "働ける" → slightly willing (0.2–0.6)
    - "できれば入りたくない" → slightly unwilling (-0.6 to -0.2)
    - "無理" or "絶対無理" → very unwilling (-1.0 to -0.6)
    - "一番嬉しい" or "大好き" → very willing (0.6–1.0)
    Instructions:
    1. Never hallucinate information; only use what is explicitly stated.
    2. Identify willingness at the phrase level in the input text.
    3. Resolve conflicts using the precedence rules above.
    4. Only return the JSON object; do not include any explanations or extra text.
    """
    main_context = main_context_1 + main_context_2
    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": main_context},
            {"role": "user", "content": text_input},
        ],
        response_format=EmployeeWillingness,
    )
    employee_pref = response.choices[0].message.parsed
    employee_dict = {emp.id: emp.willingness for emp in employee_pref.employees}
    print("________________________________")
    print(f"Input Text:{text_input} year:{employee_list}")
    print(employee_dict)
    print("________________________________")
    return employee_dict

# --- FastAPI App ---

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "description": "API for context extraction from user text.",
        "endpoints": {
            "/get_matrix": "must pass in which_matrix parameter: ee(Employee-Employee) or ed(Employee-Days) to get respective matrix.",
            "/status/{task_id}": "Check the status of a processing task."
        }
    }

@app.post("/get_matrix")
async def process_input(
    metadata: str | None = Form(None),
    year: int = Form(2025),
    month: int = Form(2),
    content: UploadFile = Form(...),
    which_matrix: str = Form(...),
    employees: str = Form(None),
):
    if content is None:
        text_input = "月曜は入れるけどできれば入りたくないです。火水木は入れます。でも一番嬉しいのは日曜日です。従業員1さんと働きたいです。従業員2さんは無理です。"   # "No particular preference" in Japanese
    else:
        try:
            text_input = (await content.read()).decode("utf-8")
            if not text_input.strip():
                text_input = "月曜は入れるけどできれば入りたくないです。火水木は入れます。でも一番嬉しいのは日曜日です。従業員1さんと働きたいです。従業員2さんは無理です。"  # "No particular preference" in Japanese
        except Exception as e:
            text_input = "月曜は入れるけどできれば入りたくないです。火水木は入れます。でも一番嬉しいのは日曜日です。従業員1さんと働きたいです。従業員2さんは無理です。" 

    if which_matrix == 'ee':
        if not employees:
            # Default employee list
            employee_list = ["従業員1", "従業員2", "従業員3"]
        else:
            try:
                employee_list: List[str] = json.loads(employees)
                if not isinstance(employee_list, list) or len(employee_list) == 0:
                    employee_list = ["従業員1", "従業員2", "従業員3"]
                if not all(isinstance(e, str) for e in employee_list):
                    employee_list = ["従業員1", "従業員2", "従業員3"]
            except json.JSONDecodeError as e:
                employee_list = ["従業員1", "従業員2", "従業員3"]
        proc_func = EE_matrix
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(
            executor,
            partial(
                proc_func,
                text_input=text_input,
                employee_list=employee_list,
            )
        )
        task_id = str(uuid.uuid4())
        tasks[task_id] = future
    elif which_matrix == 'ed':
        proc_func = ED_matrix
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(
            executor,
            partial(
                proc_func,
                text_input=text_input,
                year=year,
                month=month,
            )
        )
        task_id = str(uuid.uuid4())
        tasks[task_id] = future
    else:
        raise HTTPException(status_code=400, detail="which_matrix must be 'ed' or 'ee'.")
    
    return {"task_id": task_id, "status": "processing"}


@app.get("/status/{task_id}")
async def status(task_id: str):
    future = tasks.get(task_id)
    if not future:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # CORRECTED: asyncio.Future doesn't have a .running() method.
    # The correct way to check is to see if it's done(). If not, it's running.
    if future.done():
        try:
            result = future.result()
            return {"status": "done", "result": result}
        except Exception as e:
            return {"status": "error", "detail": str(e)}
    else:
        return {"status": "running"}

