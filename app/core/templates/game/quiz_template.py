from app.configs.yaml import cfg

# шаблон викторины
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
        f"<b>Вопрос</b>: {question}\n\n"
        f"<b>Правильный ответ</b>: {correct_answer}\n\n"
        f"<b>Твой выбор</b>: {user_choice}\n\n"
        f"<b>Статус</b>: {status_text}\n"
        f"<b>╰──────────────────╯</b>\n\n"
        f"<tg-emoji emoji-id=\"5864068125112144897\">💸</tg-emoji> <b>Получено бабла</b>: {earned} BlazeCoin"
    )

    return result_text