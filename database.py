from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from thefuzz import process  # 導入模糊比對工具
import os

# --- 1. 抽卡判定邏輯 (清單化以利比對) ---
# 將原本的正則字串改為清單，模糊比對效果更好
STANDARD_WEAPONS = ["阿莫斯之弓", "天空之翼", "四風原典", "和璞鳶", "狼的末路", "風鷹劍", "天空之卷", "天空之脊", "天空之傲", "無工之劍"]
STANDARD_CHARACTERS = ["迪盧克", "琴", "七七", "莫娜", "刻晴", "提納里", "迪希雅", "魈", "鍾離"]

def check_is_up(item_name: str, pool_type: str) -> int:
    """
    使用模糊比對判定是否為常駐。回傳 0 代表歪了，1 代表中 UP。
    """
    if not item_name: return 1
    name = item_name.strip()
    
    # 選擇比對清單
    target_list = STANDARD_WEAPONS if pool_type == "weapon" else STANDARD_CHARACTERS
    
    # 1. 先做完全一致比對 (支援單字角色如「魈」)
    if name in target_list:
        return 0
        
    # 2. 模糊比對 (處理「迪西雅」、「七七七」等錯字)
    # score 門檻設為 80，代表 80% 相似即判定為該常駐角色
    best_match, score = process.extractOne(name, target_list)
    if score >= 80:
        return 0 
        
    return 1

# --- 2. 資料庫連線設定 (保留原本雲端版邏輯) ---

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
