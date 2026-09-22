from html import escape
from app.configs.yaml_loader import cfg

def quiz_result_text(
        question: str,
        correct_answer: str,
        user_choice: str,
        is_correct: bool,
        earned: int
) -> str:

    status_text = (
        cfg['message']['quiz']['right']
        if is_correct
        else cfg['message']['quiz']['incorrect']
    )

    result_text = (
        f"<b>╭──────────────────╮</b>\n"
        f"<tg-emoji emoji-id=\"6030848053177486888\">❓</tg-emoji> <b>Вопрос</b>: {escape(question)}\n\n"
        f"<tg-emoji emoji-id=\"5260726538302660868\">✅</tg-emoji> <b>Правильный ответ</b>: {escape(correct_answer)}\n\n"
        f"<tg-emoji emoji-id=\"5276107052412859621\">👉</tg-emoji> <b>Твой выбор</b>: {escape(user_choice)}\n\n"
        f"<tg-emoji emoji-id=\"5936143551854285132\">📊</tg-emoji> <b>Статус</b>: {status_text}\n"
        f"<b>╰──────────────────╯</b>\n\n"
        f"<tg-emoji emoji-id=\"5864068125112144897\">💸</tg-emoji> <b>Получено денег</b>: {earned} BlazeCoin"
    )

    return result_text