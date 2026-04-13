import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
# print(f"Key: {key[:10]}...") 

try:
    supabase: Client = create_client(url, key)
    print("Connecting to agent_memory...")
    response = supabase.table("agent_memory").select("*").limit(1).execute()
    print("Success!")
    print(response.data)
except Exception as e:
    print(f"Error: {e}")
