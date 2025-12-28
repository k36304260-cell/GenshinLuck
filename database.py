import re

# 這裡放入你之前在 Excel 用的模糊字根
STANDARD_WEAPONS = "阿莫斯|天空|四風|和璞|狼的|風鷹|卷|脊|傲|刃"
STANDARD_CHARACTERS = "迪盧克|琴|七七|莫娜|刻晴|提納里|迪希雅"

def check_is_up(item_name: str, pool_type: str) -> int:
    """
    回傳 1 代表中 UP，0 代表歪了
    """
    if pool_type == "weapon":
        # 如果名字裡包含常駐武器關鍵字，回傳 0
        if re.search(STANDARD_WEAPONS, item_name):
            return 0
        return 1
    else:
        # 角色池判定
        if re.search(STANDARD_CHARACTERS, item_name):
            return 0
        return 1