from app.configs.yaml import cfg
from app.types.entities import UserData

from app.utils.format_num import format_num
from app.utils.truncate_name import truncate_text

BAL_TEXT = cfg['message']['balance']['balance_text']
TOP_BALANCE_TEXT = cfg['message']['balance']['top_balance_text']

# шаблон для балика
def process_balance(user: UserData, from_top: bool = False) -> str:
    money = format_num(user.money)
    text_template = (TOP_BALANCE_TEXT if from_top else BAL_TEXT)

    return text_template.format(name=truncate_text(user.name), money=money)