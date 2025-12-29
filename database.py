from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from thefuzz import process 
import os

# --- 1. 抽卡判定邏輯 (精準名單更新) ---
# 包含您指定的 10 把常駐武器
STANDARD_WEAPONS = [
    "阿莫斯之弓", "天空之翼", "四風原典", "天空之卷", 
    "和璞鳶", "天空之脊", "狼的末路", "天空之傲", 
    "風鷹劍", "天空之刃"
]
# 常駐角色名單
STANDARD_CHARACTERS = ["刻晴", "迪盧克", "七七", "琴", "莫娜", "提納里", "迪希雅", "夢見月瑞希"]

def check_is_up(item_name: str, pool_type: str) -> int:
    """判定是否中 UP。回傳 0 代表歪了 (常駐)，1 代表中 UP。"""
    if not item_name: return 1
    name = item_name.strip()
    target_list = STANDARD_WEAPONS if pool_type == "weapon" else STANDARD_CHARACTERS
    
    # 1. 優先完全一致比對
    if name in target_list:
        return 0
        
    # 2. 模糊比對 (處理打錯字的情況)
    result = process.extractOne(name, target_list)
    if result and result[1] >= 80:
        return 0 
    return 1

# --- 2. 資料庫連線設定 (保持不變) ---
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./genshin_luck.db")
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
