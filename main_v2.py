from dotenv import load_dotenv                     # Load environment variables

load_dotenv(override=True)                        # Load .env values and override if needed

#from langchain import hub
from langchain_classic import hub              # Load prompts from LangChain Hub (v1-compatible)
from langchain_classic.agents import AgentExecutor        # Core agent execution engine
from langchain_classic.agents import create_react_agent   # Modern import for creating a ReAct agent
from langchain_openai import ChatOpenAI           # OpenAI Chat model wrapper
from langchain_tavily import TavilySearch         # Tavily internet search tool

# --- Runnable wrapper (THE FIX) ---
from langchain_core.runnables import RunnableLambda # Wraps any callable as a Runnable for clean tracing

tools = [TavilySearch()]                           # Tool list for the agent

llm = ChatOpenAI(model="gpt-4")             # Instantiates the LLM that will reason and decide actions

react_prompt = hub.pull("hwchase17/react")  # Pulls the official ReAct prompt template from LangChain Hub
                                            # This prompt enforces:
                                            # Thought → Action → Observation → Final Answer format


agent = create_react_agent(llm, tools, react_prompt)  # Creates a ReAct agent by combining the LLM (reasoning), tools (actions), and the ReAct prompt (Thought→Action→Observation loop)

agent_executor = AgentExecutor(                        # Instantiates the agent runtime that controls execution and looping
    agent=agent,                                       # Injects the ReAct agent logic (the decision-making brain)
    tools=tools,                                       # Provides the list of tools the agent is allowed to use during execution
    verbose=True                                       # Enables detailed logs showing Thought, Action, and Observation steps
)

# agent_executor.invoke({"input": "What is LangChain?"}) # Starts the ReAct loop with user input; the agent reasons, calls tools if needed, observes results, and returns a final answer
# chain=agent_executor

# -------------------------------
# Runnable root wrapper (FIX)
# -------------------------------
# Why: PromptTemplate is not runnable. AgentExecutor (classic) may not show as a clean
# top-level runnable in LangSmith. Wrapping the invoke call creates a single Runnable root run.
chain = RunnableLambda(lambda x: agent_executor.invoke(x)) # ✅ LangSmith will now show a replayable Runnable run





# A to chat, K to generate                   # VS Code / Jupyter shortcut hint (not used by Python)


# -------------------------------
# Main application entry point
# -------------------------------       
def main(): # Define main function
    result = chain.invoke({ # Invoke the agent with user input
"input": "search for 3 job postings for an AI engineer using LangChain in the Bay Area"
})
    print(result) # Print final agent response


# -------------------------------
# Python entry-point guard
# -------------------------------
if __name__ == "__main__": # Ensure script runs only when executed directly
    main() # Call main function










# from dotenv import load_dotenv

# load_dotenv()

# from langchain.agents import create_agent
# from langchain_openai import ChatOpenAI
# from langchain_tavily import TavilySearch

# from schemas import AgentResponse

# tools = [TavilySearch()]
# llm = ChatOpenAI(model="gpt-4o")


# agent = create_agent(
#     model=llm,
#     tools=tools,
#     response_format=AgentResponse,
# )


# def main():
#     result = agent.invoke(
#         {
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": "search for 3 job postings for an ai engineer using langchain in the bay area on linkedin and list their details",
#                 }
#             ]
#         }
#     )
#     # Access structured response from the agent
#     structured = result.get("structured_response", None)
#     print(structured if structured is not None else result)


# if __name__ == "__main__":
#     main()
