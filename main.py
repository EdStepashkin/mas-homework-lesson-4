from agent import agent
from langchain_core.messages import AIMessage, ToolMessage

def main():
    print("Research Agent with Custom ReAct Loop (type 'exit' to quit)")
    print("-" * 40)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        # Виклик нашого власного ReAct Loop
        for msg in agent.stream(user_input):
            if isinstance(msg, AIMessage):
                # Якщо агент відповідав текстом
                if msg.content:
                    print(f"\n🤖 Агент: {msg.content}")

                # Якщо агент вирішив використати інструмент (tool calling)
                if getattr(msg, "tool_calls", None):
                    for tc in msg.tool_calls:
                        print(f"\n🔧 Tool call: {tc['name']}(**{tc['args']})")

            elif isinstance(msg, ToolMessage):
                # Коли інструмент відпрацював і повернув результат
                # Обрізаємо вивід до 150 символів, щоб не засмічувати консоль
                snippet = str(msg.content).replace('\n', ' ')[:150]
                print(f"📎 Result: {snippet}...")

if __name__ == "__main__":
    main()