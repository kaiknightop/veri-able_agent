import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Make a request
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Say hello like a cool AI agent."}
    ],
    model="llama-3.3-70b-versatile"
)

print(response.choices[0].message.content)