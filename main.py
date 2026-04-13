import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from supabase import create_client, Client



# Load environment variables
load_dotenv()

# Ensure API key(s) are set
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")


# Supabase setup
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
session_id = "user_1"  # temp📌📌📌📌📌📌
# debug 1
print("Fetching memory...")

# Create memory functions
def load_memory(session_id):
    response = supabase.table("agent_memory") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at") \
        .execute()

    messages = []
    for row in response.data:
        messages.append(f"{row['role']}: {row['content']}")

    return "\n".join(messages)


def save_memory(session_id, role, content):
    supabase.table("agent_memory").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()

# debug 2
response = supabase.table("agent_memory").select("*").execute()
print(response)

# Initialize LLMs (Multi-Model Strategy to avoid Rate Limits)
# 1. High-Performance model for research
researcher_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    max_tokens=4012,
    temperature=0.1
)

# 2. Efficient model for summarization
writer_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    max_tokens=2048,
    temperature=0.5
)


# Initialize web-search tool
search_tool = SerperDevTool()


# Research Agent
researcher = Agent(
    role="Research Analyst",
    goal="Find accurate and useful information on a given topic",
    backstory="You are a skilled researcher who gathers concise and relevant information.",
    tools=[search_tool],
    llm=researcher_llm,
    verbose=True,
    allow_delegation=False  # 👈 reduces weird behavior
)

# Writer Agent
writer = Agent(
    role="Content Writer",
    goal="Write a clear and engaging summary based on research",
    backstory="You turn research into simple, readable summaries.",
    llm=writer_llm,
    verbose=True
)

# Research Task (with web tool)
past_context = load_memory(session_id)

research_task = Task(
    description=(
        f"Here is previous conversation context:\n{past_context}\n\n"
        "Use the search tool to find recent information about the Nigerian e-commerce market. "
        "Then return a clear list of insights, trends, and statistics."
    ),
    expected_output="A concise list of current trends, stats, and insights about Nigerian e-commerce",
    agent=researcher
)

# Writing Task (FIXED ✅ expected_output added)
write_task = Task(
    description="Summarize the research into a short, clean paragraph.",
    expected_output="A concise summary paragraph (5-6 sentences max)",
    agent=writer,
    context=[research_task] 
)

# Crew Setup
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True
)

# Run Crew
result = crew.kickoff()

# Save interaction
save_memory(session_id, "user", "Tell me about Nigerian e-commerce")
save_memory(session_id, "agent", str(result))

print("\nFinal Output:\n")
print(result)