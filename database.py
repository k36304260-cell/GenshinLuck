from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import re

# --- 1. 抽卡判定邏輯 (保留您原始的功能) ---
STANDARD_WEAPONS = "阿莫斯|天空|四風|和璞|狼的|風鷹|卷|脊|傲|刃"
STANDARD_CHARACTERS = "迪盧克|琴|七七|莫娜|刻晴|提納里|迪希雅"

def check_is_up(item_name: str, pool_type: str) -> int:
    """
    回傳 1 代表中 UP，0 代表歪了
    """
    if pool_type == "weapon":
        if re.search(STANDARD_WEAPONS, item_name):
            return 0
        return 1
    else:
        if re.search(STANDARD_CHARACTERS, item_name):
            return 0
        return 1

# --- 2. 資料庫連線設定 (升級雲端版) ---

# 自動判斷 Render 的環境變數 DATABASE_URL，若無則用本地 SQLite
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./genshin_luck.db")

# 修正 PostgreSQL 網址前綴相容性
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 根據資料庫類型建立引擎
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 取得資料庫連線工具
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
