from sqlalchemy import Column, Integer, String, Boolean
# 改從 database.py 引用 Base，確保連線指向雲端
from database import Base

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # 保留功能
    pool = Column(String)                # 保留功能
    name = Column(String)                # 保留功能
    pulls = Column(Integer)              # 保留功能
    is_up = Column(Boolean)              # 保留功能
