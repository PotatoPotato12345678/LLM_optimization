import json
import tiktoken
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Tuple, Dict
from typing import List
import calendar
import json
def ED_generate(text_input):
    def month_days_with_weekdays(year: int, month: int):
        # Get number of days in the month
        _, num_days = calendar.monthrange(year, month)
        
        # Create a flat string with day followed by weekday abbreviation
        days_weekdays = "".join(
            f"{day}{calendar.day_abbr[calendar.weekday(year, month, day)]} "
            for day in range(1, num_days + 1)
        ).strip()
        
        return days_weekdays, num_days


    model = "gpt-5-mini-2025-08-07"
    import tiktoken
    def count_tokens(text: str, model: str = model) -> int:
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)
        return len(tokens)

    year = 2025 #Get from system
    month = 2 #Get from system
    # main_context = """Your task is to comprehend a given text input, and classify how willing someone is to work a given shift in a month. Respond with the structure as follows { "dN": {{0,0.7},{1,-0.5}}...} in the value section, {{SHIFT,WILLINGNESS},{SHIFT,WILLINGNESS}} Shift 0 = Early shift Shift 1 = Late shift Willingness can range between Very unwilling: -1.0 to -0.6 (not including -0.6) Slightly unwilling: -0.6 to -0.2 (not including -0.2) Neutral: -0.2 to 0.2 (not including 0.2) Slightly willing: 0.2 to 0.6 (not including 0.6) Very willing: 0.6 to 1.0 (including 1.0) Depending on the context of the text, first identify the willingness on a word based level ranging from Very unwilling, slightly unwilling, neutral, slightly willing, very willing. These correspond to ranges of numbers in the willingness scale. your task is then to return a number between the identified range in text and return the key-value pair of the entire month. If there is not enough information for a given day, default to neutral or 0 for that day. If the information given is not related or you cannot understand the request, respond with neutral for all days. Consider this the primary context of your task. No other response is necessary."""
    # month_context = f"This month has the following weekdays {month_days_with_weekdays(year, month)[0]} "

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

    from openai import OpenAI
    from pydantic import BaseModel
    from typing import List, Tuple
    client = OpenAI(api_key="")
    class ShiftItem(BaseModel):
        shift: int
        willingness: float

    # Define the structure for shift willingness
    match month_days_with_weekdays(year, month)[1]:
        case 28:
            class ShiftWillingness(BaseModel):
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
        case 29:
            class ShiftWillingness(BaseModel):
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
        case 30:
            class ShiftWillingness(BaseModel):
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
        case 31:
            class ShiftWillingness(BaseModel):
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

    response = client.responses.parse(
        model=model,
        input=[
            {"role": "system", "content": main_context},
            {"role": "user", "content": text_input},
        ],
        text_format=ShiftWillingness,
    )

    ED_matrix = response.output_parsed
    return ED_matrix
