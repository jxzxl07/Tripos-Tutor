from google import genai
from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key)

FLASH = "gemini-3-flash-preview"
PRO = "gemini-3.1-pro-preview"