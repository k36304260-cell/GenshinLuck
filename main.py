from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import pandas as pd
import io

from calculator import get_luck_percentile, get_rank_name
from database import check_is_up
from models import SessionLocal, Record, engine, Base

# 初始化資料庫
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. 數據總覽 (評級) ---
@app.get("/get_summary")
def get_summary(user_id: str, db: Session = Depends(get_db)):
    res = {}
    for p in ["weapon", "character"]:
        recs = db.query(Record).filter(Record.user_id == user_id, Record.pool == p).all()
        if not recs:
            res[p] = {"avg": 0, "win_rate": "0%", "rank": "尚無數據"}
            continue
        avg = sum(r.pulls for r in recs) / len(recs)
        wr = sum(1 for r in recs if r.is_up) / len(recs)
        res[p] = {
            "avg": round(avg, 1), 
            "win_rate": f"{round(wr*100, 1)}%", 
            "rank": get_rank_name(get_luck_percentile(avg, wr, p))
        }
    return res

# --- 2. 進階分析數據 (抽卡詳情分析面板) ---
@app.get("/get_advanced_stats")
def get_advanced_stats(user_id: str, db: Session = Depends(get_db)):
    all_recs = db.query(Record).filter(Record.user_id == user_id).all()
    if not all_recs:
        return {
            "win_rate": "0%", "total_pulls": 0, "total_stones": 0,
            "lucky_pool": "尚無數據", "avg_char_stone": 0, "avg_weapon_stone": 0
        }

    char_recs = [r for r in all_recs if r.pool == "character"]
    weapon_recs = [r for r in all_recs if r.pool == "weapon"]
    
    total_pulls = sum(r.pulls for r in all_recs)
    total_stones = total_pulls * 160
    
    char_up_count = sum(1 for r in char_recs if r.is_up)
    win_rate = (char_up_count / len(char_recs) * 100) if char_recs else 0
    
    avg_char_stone = (sum(r.pulls for r in char_recs) / len(char_recs) * 160) if char_recs else 0
    avg_weapon_stone = (sum(r.pulls for r in weapon_recs) / len(weapon_recs) * 160) if weapon_recs else 0
    
    lucky_item = min(all_recs, key=lambda x: x.pulls)
    
    return {
        "win_rate": f"{round(win_rate, 1)}%",
        "total_pulls": total_pulls,
        "total_stones": f"{total_stones:,}",
        "lucky_pool": f"{lucky_item.name} ({lucky_item.pulls}抽)",
        "avg_char_stone": f"{round(avg_char_stone):,}",
        "avg_weapon_stone": f"{round(avg_weapon_stone):,}"
    }

# --- 3. 歷史紀錄與管理 ---
@app.get("/get_history")
def get_history(user_id: str, db: Session = Depends(get_db)):
    return db.query(Record).filter(Record.user_id == user_id).order_by(Record.id.desc()).all()

@app.delete("/delete_pull/{record_id}")
def delete_pull(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="找不到紀錄")

@app.post("/add_pull")
def add_pull(user_id: str, name: str, pulls: int, pool: str, db: Session = Depends(get_db)):
    is_up = check_is_up(name, pool) == 1
    db.add(Record(user_id=user_id, name=name, pulls=pulls, pool=pool, is_up=is_up))
    db.commit()
    return {"status": "success"}

@app.post("/import_excel")
async def import_excel(user_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    df = pd.read_excel(io.BytesIO(contents))
    for _, row in df.iterrows():
        is_up = check_is_up(str(row['名稱']), str(row['池子'])) == 1
        db.add(Record(user_id=user_id, pool=str(row['池子']), name=str(row['名稱']), pulls=int(row['抽數']), is_up=is_up))
    db.commit()
    return {"status": "success"}

@app.get("/export_excel")
def export_excel(user_id: str, db: Session = Depends(get_db)):
    recs = db.query(Record).filter(Record.user_id == user_id).all()
    df = pd.DataFrame([{"池子": r.pool, "名稱": r.name, "抽數": r.pulls, "中UP": r.is_up} for r in recs])
    path = f"{user_id}_data.xlsx"
    df.to_excel(path, index=False)
    return FileResponse(path, filename=path)