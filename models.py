from sqlalchemy import Column, Integer, String, Float, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 建立資料庫檔案連結 (SQLite 會在同目錄生成 genshin_luck.db)
SQLALCHEMY_DATABASE_URL = "sqlite:///./genshin_luck.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. 定義抽卡紀錄表
class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # 儲存帳號 UID 或自定義名稱
    pool = Column(String)                # 池子類型 (weapon / character)
    name = Column(String)                # 五星物品名稱
    pulls = Column(Integer)             # 消耗抽數
    is_up = Column(Boolean)              # 是否為當期 UP (自動判定結果)

# 3. 建立表格
def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()