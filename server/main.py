from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import hashlib
import shutil
import os
import uuid
import uvicorn

#Intializing FastAPI app
app = FastAPI(title="ByteChain Verify API")

# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], #development server( gotta change for deployment)
    allow_credentials=Truec,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)


#  SQLite Database
DATABASE_URL = "sqlite:///./bytechain.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#  Db Model
class MediaLog(Base):
    __tablename__ = "media_logs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_hash = Column(String, unique=True, index=True)
    ai_confidence_score = Column(Float)
    is_tampered = Column(Integer) # 0 or 1
    upload_timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#  Cryptographic Utility Function (SHA-256)
async def compute_sha256_async(file_path: str) -> str:
    """Calculates SHA-256 hash of a file async and returns the hex code."""
    sha256_hash = hashlib.sha256()
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(8192):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

import aiofiles


#Analyze route

def analyze_media_stub(temp_file_path: str):
    #AI logic here 
   
    return 

@app.post("/api/analyze")
async def upload_and_analyze_video(file: UploadFile = File(...)):
    
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{file_id}{file_ext}"
    temp_file_path = os.path.join(TEMP_DIR, safe_filename)

    try:
        # 2. Temporarily store the file to disk
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            while content := await file.read(8192):
                await out_file.write(content)

        # Computing SHA hash of the uploaded file
        file_hash = await compute_sha256_async(temp_file_path)

        # Ai Forensic Analysis ( abhi dummy h, change krna h ye )
        confidence_score, is_tampered_bool = analyze_media_stub(temp_file_path)
        
        # Convert boolean to DB integer
        is_tampered_db = 1 if is_tampered_bool else 0

        # Storing analsis to the db
        db = SessionLocal()
        
        # Checking if hash already exists in DB
        existing_log = db.query(MediaLog).filter(MediaLog.file_hash == file_hash).first()
        if existing_log:
            existing_log.upload_timestamp = datetime.utcnow()
            db.commit()
            log_entry = existing_log
        else:
            log_entry = MediaLog(
                filename=file.filename,
                file_hash=file_hash,
                ai_confidence_score=confidence_score,
                is_tampered=is_tampered_db
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
        
        db.close()


        # Return  JSON response to frontend
        return {
            "status": "success",
            "filename": file.filename,
            "file_hash": file_hash,
            "ai_confidence": {
                "score": confidence_score,
                "is_tampered": is_tampered_bool
            },
            "is_registered_on_chain": False, # web3 work needed here
            "timestamp": log_entry.upload_timestamp
        }

    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)