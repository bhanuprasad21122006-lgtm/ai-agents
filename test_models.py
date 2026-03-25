from dotenv import load_dotenv
import os
from google import genai
load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# ONLY test non-preview flash models
models_to_test = ['gemini-flash-latest', 'gemini-2.0-flash']

for m in models_to_test:
    print(f"Testing {m}...")
    try:
        response = client.models.generate_content(model=m, contents='hi')
        print(f" -> SUCCESS: {m}\n")
    except Exception as e:
        print(f" -> FAIL: {m} - {str(e)}\n")
