from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

from config import settings, SYSTEM_PROMPT
from tools import TOOL_SCHEMAS, TOOL_FUNCTIONS

class ResearchAgent:
    def __init__(self):
        # 1. Ініціалізуємо LLM (наш "мозок")
        self.llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            api_key=settings.api_key.get_secret_value(),
            temperature=0.2 # Низька температура для більш точної і фактологічної роботи
        )
        
        # 2. Відразу прив'язуємо інструменти (формат JSON Schema) до моделі
        self.llm_with_tools = self.llm.bind_tools(TOOL_SCHEMAS)
        
        # 3. Ініціалізуємо пам'ять сесії (простий список повідомлень)
        self.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        
    def stream(self, user_input: str):
        """
        Власний ReAct Loop (генератор для потокового виводу кроків).
        """
        # Додаємо повідомлення користувача в пам'ять
        self.messages.append(HumanMessage(content=user_input))
        
        iterations = 0
        while iterations < settings.max_iterations:
            iterations += 1
            
            # Крок 1: Викликаємо LLM з усією історією повідомлень
            # Використовуємо self.llm_with_tools, щоб модель знала про доступні інструменти
            response = self.llm_with_tools.invoke(self.messages)
            
            # Додаємо відповідь моделі в історію
            self.messages.append(response)
            
            # Віддаємо відповідь (для логування в main.py)
            yield response
            
            # Крок 2: Перевіряємо, чи вирішила модель викликати інструменти
            if not getattr(response, "tool_calls", None):
                # Якщо tool_calls немає, це означає, що модель згенерувала фінальну текстову відповідь
                # Цикл завершується
                break
                
            # Крок 3: Виконуємо інструменти (Tools)
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                # Знаходимо функцію за ім'ям
                if tool_name in TOOL_FUNCTIONS:
                    func = TOOL_FUNCTIONS[tool_name]
                    try:
                        # Викликаємо функцію з розпакованими аргументами
                        result = func(**tool_args)
                    except Exception as e:
                        # Обробка помилок
                        result = f"Помилка виконання інструменту {tool_name}: {str(e)}"
                else:
                    result = f"Помилка: інструмент {tool_name} не знайдено."
                
                # Додаємо результат виконання інструмента в історію як ToolMessage
                # Важливо: tool_call_id має співпадати з id запиту від моделі
                tool_message = ToolMessage(
                    content=str(result),
                    name=tool_name,
                    tool_call_id=tool_id
                )
                self.messages.append(tool_message)
                
                # Віддаємо повідомлення інструмента (для логування в main.py)
                yield tool_message
        
        else:
            # Якщо цикл завершився по ліміту ітерацій
            limit_msg = AIMessage(content="[Системне повідомлення] Досягнуто ліміту ітерацій. Я змушений зупинитися.")
            self.messages.append(limit_msg)
            yield limit_msg

# Експортуємо готовий інстанс агента (синглтон) для використання в main.py
agent = ResearchAgent()