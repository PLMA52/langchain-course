# from dotenv import load_dotenv
 

# load_dotenv()


# def main():
#     print("Hello from langchain-course!")
    


# if __name__ == "__main__":
#     main()

from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv(override=True)

print("ENV KEY:", repr(os.getenv("OPENAI_API_KEY")))

client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "user", "content": "Say hello from a tiny Python test script."},
    ],
)

print("RESPONSE:", resp.choices[0].message.content)

