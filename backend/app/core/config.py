import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MONGO_URI = os.getenv("MONGO_URI", "")
REDIS_URI = os.getenv("REDIS_URI", "")
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
