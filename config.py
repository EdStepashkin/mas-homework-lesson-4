from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Явно вказуємо, що цю змінну треба брати з GEMINI_API_KEY у файлі .env
    api_key: SecretStr = Field(alias="GEMINI_API_KEY")

    # Задаємо дефолтну модель, щоб не тягнути її з .env
    model_name: str = "gemini-2.5-flash"

    max_search_results: int = 5
    max_url_content_length: int = 5000
    output_dir: str = "example_output"
    max_iterations: int = 10

    # Правильний синтаксис конфігурації для Pydantic V2
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Ігнорує зайві змінні в .env, якщо вони там є
    )

# Створюємо глобальний об'єкт (синглтон), який будемо імпортувати в інші файли
settings = Settings()

# Заповнюємо базовий системний промпт (можеш доповнити його під свої потреби)
SYSTEM_PROMPT = """
Ти — дослідницький AI-агент. Твоє завдання:
1. Отримувати питання від користувача.
2. Шукати інформацію в інтернеті через web_search.
3. Читати деталі статей через read_url.
4. Аналізувати дані та зберігати фінальний структурований Markdown-звіт через write_report.

Думай покроково. Завжди відповідай українською мовою.
"""