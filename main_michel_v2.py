from typing import List

from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv(override=True)

# Import the create_agent function to create an agent
from langchain.agents import create_agent

# Import the @tool decorator to define custom tools for the agent
from langchain.tools import tool

# Import HumanMessage to format messages that will be sent to the agent
from langchain_core.messages import HumanMessage

# Import ChatOpenAI to connect to OpenAI's language models
from langchain_openai import ChatOpenAI

# Import TavilyClient to use Tavily's real search API
from tavily import TavilyClient


# Initialize the Tavily client for actual web searches
# This will use the TAVILY_API_KEY from your .env file
tavily = TavilyClient()


# The @tool decorator converts this function into a tool the agent can use
@tool
def search(query: str) -> str:
    """
    Tool that searches over internet
    Args:
        query: The query to search for
    Returns:
        The search result
    """
    # Print what we're searching for (for debugging/tracking)
    print(f"Searching for {query}")
    
    # Use Tavily's search API to get real search results from the internet
    return tavily.search(query=query)


# Initialize the Large Language Model (LLM) using OpenAI's GPT-5
# This will use the OPENAI_API_KEY from your .env file
llm = ChatOpenAI(model="gpt-5")

# Create a list of tools that the agent can use
# In this case, we only have the "search" tool
tools = [search]

# Create the agent by combining the model (LLM) and tools
# The agent will automatically decide when to use the search tool
agent = create_agent(model=llm, tools=tools)


# Define the main function that will run our program
def main():
    # Print a welcome message
    print("Hello from langchain-course!")
    
    # Invoke the agent with a question
    # We pass a HumanMessage containing our question
    # The agent will process the question and decide if it needs to use the search tool
    result = agent.invoke({"messages": HumanMessage(content="What is the weather in Tokyo?")})
    
    # Print the final result from the agent
    print(result)


# This is Python's standard entry point
# It ensures main() only runs when this script is executed directly
# (not when imported as a module)
if __name__ == "__main__":
    main()





# from langchain.agents import create_agent
# from langchain.tools import tool
# from langchain_core.messages import HumanMessage
# from langchain_openai import ChatOpenAI
# from langchain_tavily import TavilySearch


# class Source(BaseModel):
#     """Schema for a source used by the agent"""

#     url: str = Field(description="The URL of the source")


# class AgentResponse(BaseModel):
#     """Schema for agent response with answer and sources"""

#     answer: str = Field(description="Thr agent's answer to the query")
#     sources: List[Source] = Field(
#         default_factory=list, description="List of sources used to generate the answer"
#     )


# llm = ChatOpenAI(model="gpt-5")
# tools = [TavilySearch()]
# agent = create_agent(model=llm, tools=tools, response_format=AgentResponse)


# def main():
#     print("Hello from langchain-course!")
#     result = agent.invoke(
#         {
#             "messages": HumanMessage(
#                 content="search for 3 job postings for an ai engineer using langchain in the bay area on linkedin and list their details?"
#             )
#         }
#     )
#     print(result)


# if __name__ == "__main__":
#     main()
