from app.configs.yaml_loader import cfg
from app.types.entities.user import UserData

from app.utils.format_num import format_num
from app.utils.truncate_name import truncate_text

BAL_TEXT = cfg['message']['balance']['balance_text']
TOP_BALANCE_TEXT = cfg['message']['balance']['top_balance_text']

def process_balance(user: UserData, from_top: bool = False) -> str:
    money = format_num(user.money)

    user_link = (
        f'<a href="tg://user?id={user.telegram_id}">'
        f'<b>{truncate_text(user.name)}</b></a>'
    )

    text_template = (TOP_BALANCE_TEXT if from_top else BAL_TEXT)

    return text_template.format(user_link=user_link, money=money)