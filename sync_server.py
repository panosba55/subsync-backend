import os
import tempfile
import subprocess
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

app = FastAPI(title="SubSync Pro - Python Sync Engine")

# Επιτρέπουμε τις κλήσεις από το Web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/sync", response_class=PlainTextResponse)
async def sync_subtitles(
    audio: UploadFile = File(...),
    srt: UploadFile = File(...)
):
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = os.path.join(temp_dir, "input_audio.mp3")
        srt_in_path = os.path.join(temp_dir, "input.srt")
        srt_out_path = os.path.join(temp_dir, "output_synced.srt")

        # Αποθήκευση προσωρινών αρχείων
        with open(audio_path, "wb") as f:
            f.write(await audio.read())
        with open(srt_in_path, "wb") as f:
            f.write(await srt.read())

        # Κλήση ffsubsync
        cmd = [
            "ffsubsync",
            audio_path,
            "-i", srt_in_path,
            "-o", srt_out_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0 or not os.path.exists(srt_out_path):
            raise HTTPException(
                status_code=500,
                detail=f"FFsubsync execution failed: {result.stderr}"
            )

        with open(srt_out_path, "r", encoding="utf-8", errors="replace") as f:
            synced_content = f.read()

        return synced_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("sync_server:app", host="0.0.0.0", port=8000, reload=True)