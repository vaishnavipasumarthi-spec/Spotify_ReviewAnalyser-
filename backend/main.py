import os
import subprocess
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import json

app = FastAPI(title="Spotify Review Discovery API")

class AnalyzeRequest(BaseModel):
    limit: int = 500

@app.get("/")
def read_root():
    return {"message": "Spotify Review Discovery API is running"}

@app.post("/analyze")
def trigger_analysis(background_tasks: BackgroundTasks, request: AnalyzeRequest = None):
    """
    Triggers the full processing pipeline in the background.
    """
    if request is None:
        request = AnalyzeRequest()
        
    def run_pipeline():
        try:
            # Phase 1: Scraper
            subprocess.run(["python", "Phase1_Data_Acquisition/scraper.py"], check=True)
            # Phase 2: Processor
            subprocess.run(["python", "Phase2_Data_Processing/processor.py"], check=True)
            # Phase 3: Theme Engine
            subprocess.run(["python", "Phase3_Theme_Generation/theme_engine.py"], check=True)
            # Phase 4: Reporter
            subprocess.run(["python", "Phase4_Synthesis_Reporting/reporter.py"], check=True)
            print("Pipeline completed via FastAPI background task.")
        except Exception as e:
            print(f"Pipeline error: {e}")

    background_tasks.add_task(run_pipeline)
    return {"status": "Analysis triggered in background", "limit": request.limit}

@app.get("/results")
def get_results():
    path = "data/themed_reviews.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Analysis results not found. Trigger analysis first.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/report")
def get_report():
    path = "reports/weekly_note.md"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Weekly report not found. Trigger analysis first.")
    with open(path, "r", encoding="utf-8") as f:
        return {"content": f.read()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
