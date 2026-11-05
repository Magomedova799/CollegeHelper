
import re
import json
import time
from pathlib import Path

import httpx


OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

# Загружаем базу знаний колледжа
KNOWLEDGE_PATH = Path(__file__).with_name("knowledge.txt")
KNOWLEDGE = KNOWLEDGE_PATH.read_text(encoding="utf-8")


def get_matching_sections(message: str) -> list[tuple[str, str]]:
    """
    Находит разделы базы знаний, соответствующие сообщению студента.
    Возвращает заголовки и оригинальный текст разделов.
    """

    parts = re.split(r"(?m)^={10,}\s*$", KNOWLEDGE)

    sections = []

    for i in range(1, len(parts) - 1, 2):
        heading = parts[i].strip()
        content = parts[i + 1].strip()

        if heading and content:
            sections.append((heading, content))

    keywords = {
        "проектор": [
            "проектор", "hdmi", "vga", "проекция",
            "подключить ноутбук", "подключение к проектору"
        ],
        "принтер": [
            "принтер", "печать", "печатает", "мфу",
            "картридж", "очередь печати"
        ],
        "компьютер": [
            "компьютер", "ноутбук", "клавиатура",
            "мышь", "usb", "завис", "не включается"
        ],
        "неисправность": [
            "не работает", "неисправность", "ошибка",
            "перегрев", "дым", "повреждение"
        ]
    }

    message_lower = message.lower()
    selected = []

    for heading, content in sections:
        heading_lower = heading.lower()

        # Правила работы ИИ передаём модели отдельно
        if "правила работы ии-помощника" in heading_lower:
            selected.append((heading, content))
            continue

        for topic, words in keywords.items():
            if any(word in message_lower for word in words):
                if topic in heading_lower:
                    selected.append((heading, content))
                    break

    return selected


def get_relevant_knowledge(message: str) -> str:
    """
    Формирует контекст из найденных разделов для Ollama.
    """

    selected = get_matching_sections(message)

    if not selected:
        return (
            "Подходящая инструкция не найдена. "
            "Не придумывай правила колледжа."
        )

    return "\n\n".join(
        heading + "\n" + content
        for heading, content in selected
    )


def get_exact_answer(message: str) -> str | None:
    """
    Возвращает оригинальный текст инструкции из knowledge.txt.
    Не перефразирует и не изменяет его.
    """

    selected = [
        (heading, content)
        for heading, content in get_matching_sections(message)
        if "правила работы ии-помощника" not in heading.lower()
    ]

    if not selected:
        return None

    return "\n\n".join(
        heading + "\n" + content
        for heading, content in selected
    )


SYSTEM_PROMPT = """
Ты ИИ-помощник колледжа CollegeHelper.

Твоя задача — помогать студентам с вопросами
об оборудовании и оформлением заявок.

ПРАВИЛА:
1. Всегда отвечай на русском языке.
2. Используй базу знаний при ответах.
3. Пиши кратко, понятно и грамотно.
4. Не придумывай информацию.
5. Если информации нет в базе знаний, честно сообщи об этом.
6. Не предлагай студенту самостоятельно ремонтировать оборудование.
7. Не утверждай, что заявка уже создана.
8. Никогда не используй фразы "Ответ студенту",
   "Ответ пользователя" или другие шаблонные заглушки.
9. Поле answer всегда должно содержать полноценный,
   осмысленный ответ именно на сообщение студента.
10. Если сообщение непонятное или бессмысленное,
    попроси студента сформулировать вопрос яснее.
11. Не повторяй текст системного промпта.
12. Не копируй примеры JSON из инструкции.

ОПРЕДЕЛИ ТИП СООБЩЕНИЯ:

information — студент задаёт вопрос или просит инструкцию.

malfunction — студент сообщает о реально возникшей
неисправности оборудования.

danger — студент сообщает о потенциально опасной ситуации.

ПРИМЕРЫ:

"Как подключить ноутбук к проектору?"
type: information
suggest_create_request: false

"У меня не работает принтер."
type: malfunction
suggest_create_request: true

"Проектор перестал показывать изображение."
type: malfunction
suggest_create_request: true

"Из оборудования идёт дым."
type: danger
human_review: true

ДОПОЛНИТЕЛЬНЫЕ ПРАВИЛА:

- Если студент просто спрашивает, что делать при неисправности,
  это information, если он не сообщает о реальной проблеме.
- При information не предлагай заявку без просьбы студента.
- При malfunction предложи оформить заявку.
- При danger рекомендуй не пользоваться оборудованием
  и обратиться к ответственному сотруднику.
- Если студент хочет оформить заявку, помоги перейти
  к странице её создания.
- Если информации недостаточно, задай уточняющий вопрос.

Верни только JSON:

{{
    "type": "information",
    "answer": "Здравствуйте! Чем могу вам помочь?",
    "category": null,
    "confidence": 0.9,
    "suggest_create_request": false,
    "draft": null,
    "needs_clarification": false,
    "human_review": false
}}

Для malfunction:
- type = "malfunction"
- suggest_create_request = true

Для danger:
- type = "danger"
- human_review = true

Не добавляй текст за пределами JSON.
"""


async def classify_message(message: str):
    relevant_knowledge = get_relevant_knowledge(message)

    print("Размер выбранной базы:", len(relevant_knowledge), "символов")
    print("Размер системного промпта:", len(SYSTEM_PROMPT), "символов")

    prompt = f"""
{SYSTEM_PROMPT}

РЕЛЕВАНТНАЯ ИНФОРМАЦИЯ ИЗ БАЗЫ ЗНАНИЙ:
{relevant_knowledge}

Сообщение студента:
{message}

Верни полный JSON без пояснений.
"""

    start_time = time.perf_counter()

    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "keep_alive": "10m",
                "options": {
                    "num_predict": 300,
                    "temperature": 0.1
                }
            }
        )

    response.raise_for_status()

    result = response.json()

    print(
        "Общее время Ollama:",
        result.get("total_duration", 0) / 1_000_000_000,
        "сек."
    )

    print(
        "Загрузка модели:",
        result.get("load_duration", 0) / 1_000_000_000,
        "сек."
    )

    print(
        "Обработка запроса:",
        result.get("prompt_eval_duration", 0) / 1_000_000_000,
        "сек."
    )

    print(
        "Генерация ответа:",
        result.get("eval_duration", 0) / 1_000_000_000,
        "сек."
    )

    print(
        f"Время ответа Ollama: "
        f"{time.perf_counter() - start_time:.2f} сек."
    )

    print("Причина завершения:", result.get("done_reason"))
    print("Выходные токены:", result.get("eval_count"))

    if not result.get("done"):
        raise ValueError("Ollama не завершила генерацию")

    answer = result["response"]

    try:
        assistant_result = json.loads(answer)

        # Получаем дословную инструкцию из базы знаний
        exact_answer = get_exact_answer(message)

        if exact_answer is not None:
            assistant_result["answer"] = exact_answer

        return assistant_result

    except json.JSONDecodeError as error:
        print("Некорректный JSON от Ollama:", answer)
        raise ValueError("Модель вернула неполный JSON") from error
