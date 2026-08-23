from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ByteChain Verify API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],#development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_video(file: UploadFile = File(...)):
    #Ai logic to analyze the video or image 
    
    return {
        "filename": file.filename, 
        "is_tampered": False, 
        "confidence_score": 0.98,
        "sha256_hash": "mock_hash_123"
    }