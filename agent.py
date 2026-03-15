from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from config import settings, SYSTEM_PROMPT
from tools import web_search, read_url, write_report, get_current_time, read_local_file

# 1. Ініціалізуємо LLM (наш "мозок")
llm = ChatGoogleGenerativeAI(
    model=settings.model_name,
    api_key=settings.api_key.get_secret_value(),
    temperature=0.2 # Низька температура для більш точної і фактологічної роботи
)

# 2. Збираємо інструменти в список (наші "руки")
tools = [web_search, read_url, write_report, get_current_time, read_local_file]

# 3. Ініціалізуємо пам'ять сесії
memory = MemorySaver()

# 4. Створюємо ReAct агента (наш "оркестратор")
agent = create_react_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    prompt=SYSTEM_PROMPT
)