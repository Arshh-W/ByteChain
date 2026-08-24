from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import hashlib
import os
import uuid
import uvicorn
import aiofiles

ML_IMPORT_ERROR = None

try:
    try:
        from server.ai_engine import predict_image
    except ImportError:
        from ai_engine import predict_image
except Exception as exc:  # pragma: no cover - runtime guard for missing ML stack
    predict_image = None
    ML_IMPORT_ERROR = exc

# Initialize FastAPI app
app = FastAPI(title="ByteChain Verify API")

# CORS setup: Allow local dev & live Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "*"  # Allows live Netlify frontend domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(SERVER_DIR, "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

# SQLite Database setup
DATABASE_URL = "sqlite:///./bytechain.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class MediaLog(Base):
    __tablename__ = "media_logs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    file_hash = Column(String, unique=True, index=True)
    ai_confidence_score = Column(Float)
    is_tampered = Column(Integer)  # 0 or 1
    upload_timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SHA-256 Utility
async def compute_sha256_async(file_path: str) -> str:
    """Calculates SHA-256 hash of a file asynchronously."""
    sha256_hash = hashlib.sha256()
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(8192):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

@app.get("/")
def health_check():
    return {"status": "ByteChain API operational", "timestamp": datetime.utcnow()}


#Analyze route

@app.get("/")
def root():
    return {"status": "ok", "service": "ByteChain Verify API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def upload_and_analyze_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Only image files are supported")

    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{file_id}{file_ext}"
    temp_file_path = os.path.join(TEMP_DIR, safe_filename)

    try:
        # Save uploaded file temporarily to disk
        async with aiofiles.open(temp_file_path, "wb") as out_file:
            while content := await file.read(8192):
                await out_file.write(content)

        # Calculate cryptographic SHA-256 hash
        file_hash = await compute_sha256_async(temp_file_path)

        if predict_image is None:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Deepfake model backend is unavailable. "
                    f"Original error: {ML_IMPORT_ERROR}"
                ),
            )

        # Run the production deepfake detector exactly once per request
        # and derive both the legacy (confidence_score, is_tampered) and
        # the rich (prediction, fake/real_probability, face_detected, ...)
        # response fields from the same result.
        prediction = predict_image(temp_file_path)
        confidence_score = float(prediction["confidence"])
        is_tampered_bool = bool(prediction["prediction"] == "FAKE")
        is_tampered_db = 1 if is_tampered_bool else 0

        # Save result to SQLite database
        db = SessionLocal()
        try:
            existing_log = db.query(MediaLog).filter(MediaLog.file_hash == file_hash).first()
            if existing_log:
                existing_log.upload_timestamp = datetime.utcnow()
                db.commit()
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
        finally:
            db.close()

        # Contract matching frontend expected response keys
        return {
            "success": True,
            "filename": file.filename,
            "is_tampered": is_tampered_bool,
            "confidence_score": round(confidence_score, 4),
            "sha256_hash": file_hash,
            # Rich prediction fields from the production deepfake detector.
            "prediction": prediction["prediction"],
            "confidence": prediction["confidence"],
            "fake_probability": prediction["fake_probability"],
            "real_probability": prediction["real_probability"],
            "threshold": prediction["threshold"],
            "face_detected": prediction["face_detected"],
            "fallback_used": prediction["fallback_used"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# Register POST /predict as an alias of /api/analyze so the endpoint
# works for clients hitting either path. The actual implementation is
# upload_and_analyze_image above.
app.add_api_route(
    "/predict",
    upload_and_analyze_image,
    methods=["POST"],
)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)