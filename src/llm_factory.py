import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 1.0):
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER='{provider}'. "
            "Set LLM_PROVIDER=gemini or LLM_PROVIDER=groq in your .env file."
        )
