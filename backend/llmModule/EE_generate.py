import json
import logging
import tiktoken
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Tuple, Dict
from typing import List

def EE_generate(text_input, employee_list, employee_flat):
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"type(text_input) -> {type(text_input)}")

    model = "gpt-5-mini-2025-08-07"
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

    client = OpenAI(api_key=)

    class Employee(BaseModel):
        id: str
        willingness: float

    class EmployeeWillingness(BaseModel):
        employees: List[Employee]

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": main_context},
            {"role": "user", "content": text_input},
        ],
        response_format=EmployeeWillingness,
    )

    employee_pref = response.choices[0].message.parsed

    # Convert to dict if needed
    EE_matrix = {emp.id: emp.willingness for emp in employee_pref.employees}
    return EE_matrix

