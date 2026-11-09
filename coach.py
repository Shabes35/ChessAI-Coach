
from dotenv import load_dotenv
from google import genai

from prompts import COACH_PERSONA, get_coaching_instruction

load_dotenv()

client = genai.Client()


def generate_explanation(chess_data, coaching_mode="spectator"):

    mode_instruction = get_coaching_instruction(coaching_mode)

    prompt = f"""
    {COACH_PERSONA}

    {mode_instruction}

    Here is the chess information:

    {chess_data}

    Important rules:
    - Use only the information provided.
    - Never invent threats, tactics, variations or strategic plans.
    - Do not reveal raw Stockfish evaluation numbers.
    - If the supplied information is insufficient to explain something,
      do not guess.
    - Keep the explanation concise, natural and beginner-friendly.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text
