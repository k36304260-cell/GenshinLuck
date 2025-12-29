from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from thefuzz import process  # 導入模糊比對工具
import os

# --- 1. 抽卡判定邏輯 ---
STANDARD_WEAPONS = ["阿莫斯之弓", "天空之翼", "四風原典", "和璞鳶", "狼的末路", "風鷹劍", "天空之卷", "天空之脊", "天空之傲", "無工之劍"]
# 確保包含「迪希雅」
STANDARD_CHARACTERS = ["迪盧克", "琴", "七七", "莫娜", "刻晴", "提納里", "迪希雅", "魈", "鍾離"]

def check_is_up(item_name: str, pool_type: str) -> int:
    """
    回傳 0 代表歪了 (常駐)，1 代表中 UP
    """
    if not item_name: return 1
    name = item_name.strip()
    
    target_list = STANDARD_WEAPONS if pool_type == "weapon" else STANDARD_CHARACTERS
    
    # 1. 完全一致比對 (最精準)
    if name in target_list:
        return 0
        
    # 2. 模糊比對 (處理「迪西雅」等錯字)
    # extractOne 會回傳 (match, score)，我們只需要 score
    result = process.extractOne(name, target_list)
    if result:
        best_match, score = result[0], result[1]
        # 如果相似度 > 80 分，判定為常駐 (歪了)
        if score >= 80:
            return 0 
        
    return 1

# --- 2. 資料庫連線設定 (保持不變) ---
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./genshin_luck.db")

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
