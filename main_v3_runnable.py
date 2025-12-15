# ===============================================================  # Visual header separator
# Consolidated Instructor Code (from your screenshots)              # Matches instructor structure
# - main.py + prompt.py + schemas.py merged into ONE FILE           # Single-file version
# - ReAct agent + TavilySearch + PydanticOutputParser               # Core components
# ===============================================================  # Visual header separator

from dotenv import load_dotenv  # Loads environment variables from a .env file

load_dotenv(
    override=True
)  # Reads .env and sets env vars (OPENAI_API_KEY, TAVILY_API_KEY, etc.)

from typing import List, Optional  # Typing helpers used in the schema

from langchain import hub  # Allows pulling prompts from LangChain Hub
from langchain.agents import \
    AgentExecutor  # Runs the agent loop (Thought → Action → Observation)
from langchain.agents.react.agent import \
    create_react_agent  # Builds a ReAct-style agent
from langchain_community.tools.tavily_search import \
    TavilySearchResults  # Tavily web search tool
from langchain_core.output_parsers.pydantic import \
    PydanticOutputParser  # Enforces structured output via Pydantic
from langchain_core.prompts import \
    PromptTemplate  # Creates a prompt template with variables
from langchain_core.runnables import \
    RunnableLambda  # (Imported in your screenshots; optional for tracing)
from langchain_openai import ChatOpenAI  # OpenAI chat model wrapper
from pydantic import (  # BaseModel defines schemas; Field adds metadata/validation
    BaseModel, Field)

# from langchain_tavily import TavilySearch  # Tavily web search tool


# ==============================  # Section separator
# schemas.py (merged)             # Pydantic schema used by PydanticOutputParser
# ==============================  # Section separator



class JobPosting(BaseModel):  # Represents one job posting item
    title: str = Field(..., description="Job title")  # Title of the job
    company: str = Field(..., description="Company name")  # Company offering the role
    location: str = Field(..., description="Job location")  # City/State/Remote, etc.
    url: str = Field(
        ..., description="Direct link to the job posting"
    )  # Apply / details link


class AgentResponse(
    BaseModel
):  # Represents the full structured response returned by the agent
    results: List[JobPosting] = Field(
        ..., description="List of job postings"
    )  # The job postings list
    notes: Optional[str] = Field(
        None, description="Any extra notes (e.g., some links may expire)"
    )  # Optional notes


# ==============================  # Section separator
# prompt.py (merged)              # ReAct prompt wrapper that injects format instructions
# ==============================  # Section separator

REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS = """ You are a helpful AI agent. You can use tools.

TOOLS:
{tools}

Use the following format:

Question: {input}
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Observation can repeat N times)

When you have the final answer, you MUST respond with:
Final Answer: <your JSON response>

Your JSON response must follow these instructions:
{format_instructions}

Begin!

Question: {input}
{agent_scratchpad}
"""  # End of the instructor-style prompt template


# ==============================  # Section separator
# main.py (merged)                # The runnable script
# ==============================  # Section separator

tools = [TavilySearchResults()]  # Tool list the agent can use
llm = ChatOpenAI(model="gpt-4")  # LLM the agent uses to reason and write responses

react_prompt = hub.pull(
    "hwchase17/react"
)  # Pulls canonical ReAct prompt from Hub (shown in screenshots)

output_parser = PydanticOutputParser(
    pydantic_object=AgentResponse
)  # Parser that forces output into AgentResponse

react_prompt_with_format_instructions = PromptTemplate(  # Build a PromptTemplate using the custom template above
    template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS,  # Prompt text with placeholders
    input_variables=[
        "input",
        "agent_scratchpad",
        "tool_names",
        "tools",
    ],  # FIX: Added "tools" to match template
).partial(  # Partially fill variables once, up-front
    format_instructions=output_parser.get_format_instructions()  # Inject schema-driven JSON instructions
)

agent = create_react_agent(  # Create the ReAct agent
    llm=llm,  # The reasoning model
    tools=tools,  # Tools the agent can call
    prompt=react_prompt_with_format_instructions,  # Prompt that includes JSON format instructions
)

agent_executor = (
    AgentExecutor(  # Create the executor that runs the loop until completion
        agent=agent,  # The agent (policy)
        tools=tools,  # Tools registry
        verbose=True,  # Print Thought/Action/Observation to the terminal
        handle_parsing_errors=True,  # Gracefully handle parsing errors
        max_iterations=15,  # FIX 1: Increase from default 10 to give agent more chances
    )
)


# ------------------------------ # Section separator
# Runnable post-processing steps # These match your latest screenshots
# ------------------------------ # Section separator


extract_output = RunnableLambda(
    lambda x: x["output"]
)  # Extract the raw "output" string from executor result dict


# FIX 2: Safe parse function that handles errors gracefully
def safe_parse(x):  # Wrapper function to catch parsing errors
    try:  # Attempt to parse
        return output_parser.parse(
            x
        )  # Parse raw output JSON -> AgentResponse Pydantic object
    except Exception as e:  # If parsing fails
        print(f"Parse failed: {e}")  # Print the error
        print(f"Raw output: {x}")  # Print what the agent returned
        return x  # Return raw output so you can still see the data


parse_output = RunnableLambda(
    safe_parse
)  # Use safe_parse instead of direct output_parser.parse


chain = (
    agent_executor | extract_output | parse_output
)  # Compose into one runnable pipeline using LCEL (| operator)


def main():  # Main function (keeps execution clean)
    result = chain.invoke(  # Invoke the agent
        input={  # Input dict passed to the agent
            "input": "search for 3 job postings for an ai engineer using langchain in the bay area on linkedin and list their details"  # User request
        }
    )
    print(result)  # Print the final structured JSON-like result


if __name__ == "__main__":  # Entry-point guard
    main()  # Run main when executed as a script


######## Alternative version below (from your earlier screenshots) ####
# # ===============================================================  # Visual header separator
# # Consolidated Instructor Code (from your screenshots)              # Matches instructor structure
# # - main.py + prompt.py + schemas.py merged into ONE FILE           # Single-file version
# # - ReAct agent + TavilySearch + PydanticOutputParser               # Core components
# # ===============================================================  # Visual header separator

# from dotenv import load_dotenv  # Loads environment variables from a .env file

# load_dotenv(override=True)  # Reads .env and sets env vars (OPENAI_API_KEY, TAVILY_API_KEY, etc.)

# from langchain import hub  # Allows pulling prompts from LangChain Hub
# from langchain.agents import AgentExecutor  # Runs the agent loop (Thought → Action → Observation)
# from langchain.agents.react.agent import create_react_agent  # Builds a ReAct-style agent
# from langchain_core.output_parsers.pydantic import PydanticOutputParser  # Enforces structured output via Pydantic
# from langchain_core.prompts import PromptTemplate  # Creates a prompt template with variables
# from langchain_core.runnables import RunnableLambda  # Wraps a function as a Runnable for LCEL pipelines
# from langchain_openai import ChatOpenAI  # OpenAI chat model wrapper
# from langchain_community.tools.tavily_search import TavilySearchResults  # Tavily web search tool (community version)
# # from langchain_tavily import TavilySearch  # Old import - not compatible with langchain 0.2.x


# # ==============================  # Section separator
# # schemas.py (merged)             # Pydantic schema used by PydanticOutputParser
# # ==============================  # Section separator

# from pydantic import BaseModel, Field  # BaseModel defines schemas; Field adds metadata/validation
# from typing import List, Optional  # Typing helpers used in the schema


# class JobPosting(BaseModel):  # Represents one job posting item
#     title: str = Field(..., description="Job title")  # Title of the job (... means required)
#     company: str = Field(..., description="Company name")  # Company offering the role
#     location: str = Field(..., description="Job location")  # City/State/Remote, etc.
#     url: str = Field(..., description="Direct link to the job posting")  # Apply / details link


# class AgentResponse(BaseModel):  # Represents the full structured response returned by the agent
#     results: List[JobPosting] = Field(..., description="List of job postings")  # The job postings list
#     notes: Optional[str] = Field(None, description="Any extra notes (e.g., some links may expire)")  # Optional notes


# # ==============================  # Section separator
# # prompt.py (merged)              # ReAct prompt wrapper that injects format instructions
# # ==============================  # Section separator

# REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS = """
# You are a helpful AI agent. You can use tools.

# TOOLS:
# {tools}

# Use the following format:

# Question: {input}
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Observation can repeat N times)

# When you have the final answer, respond ONLY with a JSON object that follows these instructions:
# {format_instructions}

# Begin!

# Question: {input}
# {agent_scratchpad}
# """  # End of the instructor-style prompt template


# # ==============================  # Section separator
# # main.py (merged)                # The runnable script
# # ==============================  # Section separator

# tools = [TavilySearchResults()]  # Tool list the agent can use (Tavily for web search)
# llm = ChatOpenAI(model="gpt-4")  # LLM the agent uses to reason and write responses

# react_prompt = hub.pull("hwchase17/react")  # Pulls canonical ReAct prompt from Hub (not used but shows how to fetch)

# output_parser = PydanticOutputParser(pydantic_object=AgentResponse)  # Parser that forces output into AgentResponse schema

# react_prompt_with_format_instructions = PromptTemplate(  # Build a PromptTemplate using the custom template above
#     template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS,  # Prompt text with placeholders
#     input_variables=["input", "agent_scratchpad", "tool_names", "tools"],  # FIX: Added "tools" to match template placeholder
# ).partial(  # Partially fill variables once, up-front
#     format_instructions=output_parser.get_format_instructions()  # Inject schema-driven JSON instructions into prompt
# )

# agent = create_react_agent(  # Create the ReAct agent
#     llm=llm,  # The reasoning model (GPT-4)
#     tools=tools,  # Tools the agent can call (TavilySearchResults)
#     prompt=react_prompt_with_format_instructions,  # Prompt that includes JSON format instructions
# )

# agent_executor = AgentExecutor(  # Create the executor that runs the loop until completion
#     agent=agent,  # The agent (policy)
#     tools=tools,  # Tools registry (must match what agent was created with)
#     verbose=True,  # Print Thought/Action/Observation to the terminal
#     handle_parsing_errors=True,  # Gracefully handle parsing errors - lets agent retry on malformed output
# )


# # ------------------------------ # Section separator
# # Runnable post-processing steps # LCEL pipeline for clean output processing
# # ------------------------------ # Section separator

# extract_output = RunnableLambda(lambda x: x["output"])  # Extract the raw "output" string from executor result dict

# parse_output = RunnableLambda(lambda x: output_parser.parse(x))  # Parse raw output JSON string -> AgentResponse Pydantic object

# chain = agent_executor | extract_output | parse_output  # Compose into one runnable pipeline using LCEL (| operator)
# # Pipeline flow: agent_executor returns dict -> extract_output gets "output" value -> parse_output converts to Pydantic


# def main():  # Main function (keeps execution clean)
#     result = chain.invoke(  # Invoke the agent
#         input={  # Input dict passed to the agent
#             "input": "search for 3 job postings for an ai engineer using langchain in the bay area on linkedin and list their details"  # User request
#         }
#     )
#     print(result)  # Print the final structured JSON-like result


# if __name__ == "__main__":  # Entry-point guard
#     main()  # Run main when executed as a script


# # ===============================================================  # Visual header separator
# # Consolidated Instructor Code (from your screenshots)              # Matches instructor structure
# # - main.py + prompt.py + schemas.py merged into ONE FILE           # Single-file version
# # - ReAct agent + TavilySearch + PydanticOutputParser               # Core components
# # ===============================================================  # Visual header separator

# from dotenv import load_dotenv  # Loads environment variables from a .env file

# load_dotenv()  # Reads .env and sets env vars (OPENAI_API_KEY, TAVILY_API_KEY, etc.)

# # from langchain import hub  # Allows pulling prompts from LangChain Hub
# from langchainhub import Client # Allows pulling prompts from LangChain Hub
# # from langchain.agents.agent import AgentExecutor  # Runs the agent loop (Thought → Action → Observation)
# from langchain_classic.agents import AgentExecutor  # Runs the agent loop (Thought → Action → Observation)
# from langchain_classic.agents.react.agent import create_react_agent  # Builds a ReAct-style agent
# from langchain_core.output_parsers.pydantic import PydanticOutputParser  # Enforces structured output via Pydantic
# from langchain_core.prompts import PromptTemplate  # Creates a prompt template with variables
# from langchain_core.runnables import RunnableLambda  # (Imported in your screenshots; optional for tracing)
# from langchain_openai import ChatOpenAI  # OpenAI chat model wrapper
# from langchain_tavily import TavilySearch  # Tavily web search tool


# # ==============================  # Section separator
# # schemas.py (merged)             # Pydantic schema used by PydanticOutputParser
# # ==============================  # Section separator

# from pydantic import BaseModel, Field  # BaseModel defines schemas; Field adds metadata/validation
# from typing import List, Optional  # Typing helpers used in the schema


# class JobPosting(BaseModel):  # Represents one job posting item
#     title: str = Field(..., description="Job title")  # Title of the job
#     company: str = Field(..., description="Company name")  # Company offering the role
#     location: str = Field(..., description="Job location")  # City/State/Remote, etc.
#     url: str = Field(..., description="Direct link to the job posting")  # Apply / details link


# class AgentResponse(BaseModel):  # Represents the full structured response returned by the agent
#     results: List[JobPosting] = Field(..., description="List of job postings")  # The job postings list
#     notes: Optional[str] = Field(None, description="Any extra notes (e.g., some links may expire)")  # Optional notes


# # ==============================  # Section separator
# # prompt.py (merged)              # ReAct prompt wrapper that injects format instructions
# # ==============================  # Section separator

# REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS = """  # Start of the instructor-style prompt template
# You are a helpful AI agent. You can use tools.

# TOOLS:
# {tools}

# Use the following format:

# Question: {input}
# Thought: you should always think about what to do
# Action: the action to take, should be one of [{tool_names}]
# Action Input: the input to the action
# Observation: the result of the action
# ... (this Thought/Action/Observation can repeat N times)

# When you have the final answer, respond ONLY with a JSON object that follows these instructions:
# {format_instructions}

# Begin!

# Question: {input}
# {agent_scratchpad}
# """  # End of the instructor-style prompt template


# # ==============================  # Section separator
# # main.py (merged)                # The runnable script
# # ==============================  # Section separator

# tools = [TavilySearch()]  # Tool list the agent can use
# llm = ChatOpenAI(model="gpt-4")  # LLM the agent uses to reason and write responses

# # react_prompt = hub.pull("hwchase17/react")  # Pulls canonical ReAct prompt from Hub (shown in screenshots)

# # react_prompt = langchainhub.pull("hwchase17/react") # Pulls canonical ReAct prompt from Hub (shown in screenshots)

# hub_client = Client()
# react_prompt = hub_client.pull("hwchase17/react")  # Pulls canonical ReAct prompt from Hub (shown in screenshots)

# output_parser = PydanticOutputParser(pydantic_object=AgentResponse)  # Parser that forces output into AgentResponse

# react_prompt_with_format_instructions = PromptTemplate(  # Build a PromptTemplate using the custom template above
#     template=REACT_PROMPT_WITH_FORMAT_INSTRUCTIONS,  # Prompt text with placeholders
#     input_variables=["input", "agent_scratchpad", "tool_names"],  # Variables filled by the agent runtime
# ).partial(  # Partially fill variables once, up-front
#     format_instructions=output_parser.get_format_instructions()  # Inject schema-driven JSON instructions
# )

# agent = create_react_agent(  # Create the ReAct agent
#     llm=llm,  # The reasoning model
#     tools=tools,  # Tools the agent can call
#     prompt=react_prompt_with_format_instructions,  # Prompt that includes JSON format instructions
# )

# agent_executor = AgentExecutor(  # Create the executor that runs the loop until completion
#     agent=agent,  # The agent (policy)
#     tools=tools,  # Tools registry
#     verbose=True,  # Print Thought/Action/Observation to the terminal
# )

# chain = agent_executor  # Alias so we can call chain.invoke(...)


# def main():  # Main function (keeps execution clean)
#     result = chain.invoke(  # Invoke the agent
#         input={  # Input dict passed to the agent
#             "input": "search for 3 job postings for an ai engineer using langchain in the bay area on linkedin and list their details"  # User request
#         }
#     )
#     print(result)  # Print the final structured JSON-like result


# if __name__ == "__main__":  # Entry-point guard
#     main()  # Run main when executed as a script
