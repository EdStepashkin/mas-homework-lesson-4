import os
from datetime import datetime
from langchain_core.tools import tool
from ddgs import DDGS
import trafilatura

# Імпортуємо наші налаштування
from config import settings

@tool
def web_search(query: str) -> list[dict]:
    """
    Виконує пошук в інтернеті за запитом.
    Повертає список знайдених сторінок із заголовком (title), посиланням (href) та коротким описом (body).
    Використовуй це для знаходження актуальної інформації.
    """
    try:
        # DDGS().text повертає генератор словників
        results = DDGS().text(query, max_results=settings.max_search_results)
        return list(results)
    except Exception as e:
        # Повертаємо помилку текстом, щоб агент не впав і міг змінити стратегію
        return [{"error": f"Помилка пошуку: {str(e)}"}]


@tool
def read_url(url: str) -> str:
    """
    Завантажує та витягує повний текст веб-сторінки за вказаним URL.
    Використовуй цей інструмент, щоб детально прочитати статтю, знайдену через web_search.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return f"Помилка: не вдалося завантажити сторінку {url}"

        # Витягуємо основний текст, ігноруючи меню та рекламу
        text = trafilatura.extract(downloaded)
        if not text:
            return f"Помилка: не вдалося витягнути текст зі сторінки {url}"

        # Context Engineering: обрізаємо текст, щоб не переповнити пам'ять агента
        if len(text) > settings.max_url_content_length:
            return text[:settings.max_url_content_length] + "\n... [ТЕКСТ ОБРІЗАНО ЧЕРЕЗ ЛІМІТ]"

        return text
    except Exception as e:
        return f"Помилка читання URL: {str(e)}"


@tool
def write_report(filename: str, content: str) -> str:
    """
    Зберігає згенерований Markdown-звіт у файл.
    Приймає назву файлу (наприклад, report.md) та текст.
    """
    try:
        # Створюємо директорію, якщо її ще немає
        os.makedirs(settings.output_dir, exist_ok=True)
        filepath = os.path.join(settings.output_dir, filename)

        # Зберігаємо файл
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Звіт успішно збережено за шляхом: {filepath}"
    except Exception as e:
        return f"Помилка збереження файлу: {str(e)}"

@tool
def get_current_time() -> str:
    """
    Повертає поточний місцевий час та дату.
    Використовуй цей інструмент, коли користувач запитує щось відносно поточного часу (наприклад, актуальні новини за сьогодні).
    """
    now = datetime.now()
    return f"Поточний час та дата: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
def read_local_file(filepath: str) -> str:
    """
    Читає вміст локального файлу (наприклад, .md, .txt) за заданим шляхом.
    Корисно, якщо потрібно проаналізувати вже існуючий звіт.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            # Обрізаємо занадто великі файли
            if len(content) > settings.max_url_content_length:
                return content[:settings.max_url_content_length] + "\n... [ТЕКСТ ОБРІЗАНО ЧЕРЕЗ ЛІМІТ]"
            return content
    except FileNotFoundError:
        return f"Помилка: Файл не знайдено за шляхом {filepath}"
    except Exception as e:
        return f"Помилка читання файлу: {str(e)}"