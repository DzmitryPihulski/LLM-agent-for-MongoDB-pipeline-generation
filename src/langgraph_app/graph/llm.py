from config import static_config
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from openai import OpenAI

# LLM that I am going to use
MistralLLM = ChatMistralAI(  # type: ignore
    model_name="mistral-large-latest",
    max_tokens=400,
    max_retries=3,
    api_key=static_config["mistral_key"],  # type: ignore
)  # type: ignore

Deepseek = OpenAI(
    api_key=static_config["deepseek_key"],
    base_url="https://api.deepseek.com",
)

OpenAI_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    max_tokens=100,
    api_key=static_config["openai_key"],
)
