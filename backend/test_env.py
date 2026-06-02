import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

print("URL:", url)
print("Key length:", len(key) if key else "None")
print("Key первые 20 символов:", key[:20] if key else "None")