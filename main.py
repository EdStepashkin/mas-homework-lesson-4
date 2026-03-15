from agent import agent

def main():
    print("Research Agent (type 'exit' to quit)")
    print("-" * 40)

    # Створюємо конфігурацію сесії.
    # thread_id може бути будь-яким унікальним рядком.
    config = {"configurable": {"thread_id": "session_1"}}

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

        # Виклик агента з потоковим виводом проміжних кроків
        for chunk in agent.stream(
                {"messages": [("user", user_input)]},
                config=config,
        ):
            # Проходимося по вузлах графа (agent або tools)
            for node_name, state in chunk.items():
                messages = state.get("messages", [])
                # Беремо останнє повідомлення з поточного стану
                if not messages:
                    continue

                msg = messages[-1]

                if node_name == "agent":
                    # Якщо агент щось каже текстом
                    if msg.content:
                        print(f"\n🤖 Агент: {msg.content}")

                    # Якщо агент вирішив використати інструмент (tool calling)
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"\n🛠️ Агент викликає: {tc['name']}")
                            print(f"   Параметри: {tc['args']}")

                elif node_name == "tools":
                    # Коли інструмент відпрацював і повернув результат
                    # Обрізаємо вивід до 150 символів, щоб не засмічувати консоль
                    snippet = str(msg.content).replace('\n', ' ')[:150]
                    print(f"\n✅ Інструмент {msg.name} повернув результат:")
                    print(f"   {snippet}...")

if __name__ == "__main__":
    main()