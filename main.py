import os
import io
import uuid
import time
import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"

app = FastAPI(title="AI Song Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve mock assets when running in mock mode
mock_dir = os.path.join(os.path.dirname(__file__), "src", "mock_assets")
if not os.path.exists(mock_dir):
    os.makedirs(mock_dir, exist_ok=True)
app.mount("/mock", StaticFiles(directory=mock_dir), name="mock")

# In-memory job store for mock-mode
JOB_STORE = {}

# Load prompts
PROMPTS = {}
try:
    with open("blueflame_prompts.json", "r") as f:
        PROMPTS = json.load(f)
except Exception:
    PROMPTS = {}

# Models
class ProjectIn(BaseModel):
    bpm: int = Field(90, ge=40, le=220)
    lyrics: str
    voice: dict
    moods: List[str] = []
    tracks: List[dict] = []

class ProjectOut(ProjectIn):
    id: str

class GenerateStepRequest(ProjectIn):
    project_id: Optional[str] = None

class JobStatus(BaseModel):
    jobId: str
    status: str
    step: str
    percent: int
    logs: List[str] = []
    masterUrl: Optional[str] = None
    videoUrl: Optional[str] = None
    verticalVideoUrl: Optional[str] = None
    promoUrl: Optional[str] = None
    stemsZipUrl: Optional[str] = None

# Utilities

def simulate_progress(job_id: str, steps: List[str]):
    total = len(steps)
    for idx, step in enumerate(steps, start=1):
        JOB_STORE[job_id]["step"] = step
        JOB_STORE[job_id]["percent"] = int(idx / total * 100 * 0.95)
        JOB_STORE[job_id]["logs"].append(f"{step} started at BPM {JOB_STORE[job_id]['bpm']}")
        time.sleep(0.8)
    # Complete
    JOB_STORE[job_id]["percent"] = 100
    JOB_STORE[job_id]["status"] = "done"
    # Provide mock assets
    JOB_STORE[job_id]["masterUrl"] = "/mock/master.mp3"
    JOB_STORE[job_id]["videoUrl"] = "/mock/video_16_9.mp4"
    JOB_STORE[job_id]["verticalVideoUrl"] = "/mock/video_9_16.mp4"
    JOB_STORE[job_id]["promoUrl"] = "/mock/promo_30s.mp4"
    JOB_STORE[job_id]["stemsZipUrl"] = "/mock/stems.zip"

# Routes
@app.get("/")
async def root():
    return {"message": "AI Song Generator Backend", "mock": MOCK_MODE}

@app.post("/api/projects", response_model=ProjectOut)
async def create_project(p: ProjectIn):
    pid = str(uuid.uuid4())
    return ProjectOut(id=pid, **p.model_dump())

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    return {"id": project_id, "exists": True}

@app.post("/api/upload/voice")
async def upload_voice(files: List[UploadFile] = File(...)):
    processed = []
    for f in files:
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in [".wav", ".mp3", ".amr"]:
            raise HTTPException(status_code=400, detail="Unsupported format. Please upload .wav, .mp3, or .amr")
        data = await f.read()
        if len(data) < 8000:
            raise HTTPException(status_code=400, detail="File too short (<0.5s). Please upload longer clips.")
        quality = {
            "sampleRate": 44100,
            "duration_ms": max(600, len(data) // 64),
            "clipping": False
        }
        processed.append({"filename": f.filename, "quality": quality})
    return {"voiceProfileId": str(uuid.uuid4()), "processedFiles": processed, "qualityReport": processed[0]["quality"] if processed else None}

@app.post("/api/generate/instrumental")
async def gen_instrumental(req: GenerateStepRequest):
    return {"status": "ok", "prompt": PROMPTS.get("instrumental"), "bpm": req.bpm}

@app.post("/api/generate/melody")
async def gen_melody(req: GenerateStepRequest):
    return {"status": "ok", "prompt": PROMPTS.get("melody-from-lyrics"), "bpm": req.bpm}

@app.post("/api/synthesize/vocal")
async def synth_vocal(req: GenerateStepRequest):
    return {"status": "ok", "prompt": PROMPTS.get("vocal_synthesis"), "bpm": req.bpm}

@app.post("/api/mix")
async def mix(req: GenerateStepRequest):
    return {"status": "ok", "prompt": PROMPTS.get("mix_and_master"), "bpm": req.bpm}

@app.post("/api/generate/video")
async def gen_video(req: GenerateStepRequest):
    return {"status": "ok", "prompt": PROMPTS.get("video_generation"), "bpm": req.bpm}

@app.delete("/api/voice/{voice_id}")
async def delete_voice(voice_id: str):
    return {"deleted": True, "voice_id": voice_id}

@app.post("/api/generate/create")
async def create(background_tasks: BackgroundTasks, req: GenerateStepRequest):
    job_id = str(uuid.uuid4())
    JOB_STORE[job_id] = {"jobId": job_id, "status": "running", "step": "Starting", "percent": 0, "logs": [], "bpm": req.bpm}
    if MOCK_MODE:
        steps = [
            "Uploading/Adapting Voice Profile",
            "Generating Instrumental",
            "Generating Melody from Lyrics",
            "Vocal Synthesis",
            "Mix & Master",
            "Video Generation"
        ]
        background_tasks.add_task(simulate_progress, job_id, steps)
        return {"jobId": job_id}
    else:
        background_tasks.add_task(simulate_progress, job_id, ["Processing"])  # placeholder
        return {"jobId": job_id}

@app.get("/api/job/{job_id}/status", response_model=JobStatus)
async def job_status(job_id: str):
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job

@app.get("/openapi-stub")
async def openapi_stub():
    return {
        "endpoints": [
            "POST /api/projects",
            "GET /api/projects/:id",
            "POST /api/upload/voice",
            "POST /api/generate/instrumental",
            "POST /api/generate/melody",
            "POST /api/synthesize/vocal",
            "POST /api/mix",
            "POST /api/generate/video",
            "POST /api/generate/create",
            "GET /api/job/:jobId/status",
            "DELETE /api/voice/:id"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
