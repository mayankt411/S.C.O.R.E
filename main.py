import time
import uuid
from typing import Dict, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.questions import get_dynamic_questions
from core.scoring_engine import ScoringEngine
from core.typing_analyzer import TypingAnalyzer
from core.ml_models.feature_extractor import FeatureExtractor
from core.ml_models.disease_predictor import DiseasePredictor
from core.data_manager import DataManager
from core.config import APP_TITLE, APP_SUBTITLE

from schemas import Question, AnswerRequest, AnswerResponse, AssessmentResult, UserProfile, LoginRequest

import numpy as np

def sanitize_data(data):
    """Recursive helper to convert non-JSON-serializable types (like numpy) to Python originals."""
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(v) for v in data]
    elif isinstance(data, (np.int64, np.int32, np.int16, np.int8)):
        return int(data)
    elif isinstance(data, (np.float64, np.float32, np.float16)):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, np.bool_):
        return bool(data)
    return data

app = FastAPI(title=APP_TITLE)

# Statics and Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Core Engine Instances (Singletons for the app)
scorer = ScoringEngine()
analyzer = TypingAnalyzer()
extractor = FeatureExtractor()
predictor = DiseasePredictor()
data_manager = DataManager()

# In-memory session store (Replace with Redis/DB for production)
sessions: Dict[str, Dict] = {}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": APP_TITLE})

@app.post("/api/login")
async def login(request: LoginRequest):
    session_id = str(uuid.uuid4())
    questions = get_dynamic_questions()
    
    sessions[session_id] = {
        "user_profile": request.model_dump(),
        "questions": questions,
        "responses": [],
        "current_idx": 0,
        "start_time": time.time(),
        "q_start_time": time.time(),
        "performance_history": []
    }
    
    return {"session_id": session_id, "user": request.name}

@app.get("/api/start/{session_id}")
async def start_assessment(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session = sessions[session_id]
    questions = session["questions"]
    
    return {"first_question": questions[0], "total_questions": len(questions)}

@app.post("/api/submit", response_model=AnswerResponse)
async def submit_answer(request: AnswerRequest):
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.session_id]
    questions = session["questions"]
    idx = session["current_idx"]
    
    if idx >= len(questions):
        raise HTTPException(status_code=400, detail="Assessment already completed")
    
    question = questions[idx]
    
    # 1. Scoring
    score, status, feedback = scorer.score(
        request.user_input, 
        question['expected_answers'], 
        q_type=question['type']
    )
    
    # 2. Typing Analysis
    expected_standard = question['expected_answers'][0] if question['expected_answers'] else ""
    typing_metrics = analyzer.analyze_response(
        request.user_input, 
        expected_standard, 
        request.duration
    )
    
    # 3. Store Response
    earned_points = score * question['points']
    response_entry = {
        "question_id": question['id'],
        "domain": question['domain'],
        "question_text": question['text'],
        "user_answer": request.user_input,
        "max_points": question['points'],
        "earned": earned_points,
        "status": status,
        "feedback": feedback,
        "time_taken": request.duration,
        "typing_metrics": typing_metrics
    }
    session["responses"].append(response_entry)
    session["performance_history"].append(score)
    
    # 4. Advance
    session["current_idx"] += 1
    session["q_start_time"] = time.time()
    
    next_question = questions[session["current_idx"]] if session["current_idx"] < len(questions) else None
    
    return sanitize_data({
        "score": score,
        "status": status,
        "feedback": feedback,
        "earned_points": earned_points,
        "typing_metrics": typing_metrics,
        "next_question": next_question,
        "is_completed": next_question is None
    })

@app.get("/api/results/{session_id}", response_model=AssessmentResult)
async def get_results(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    responses = session["responses"]
    
    # 1. Aggregate Typing Metrics
    typing_summary = analyzer.aggregate_session_metrics(responses)
    
    # 2. Extract Features
    features = extractor.extract_features(responses, typing_summary)
    
    # 3. Predict Health Outcome
    prediction = predictor.predict(features)
    
    # Store results in session for report gen
    session["prediction"] = prediction
    session["typing_summary"] = typing_summary
    
    raw_score = sum(r['earned'] for r in responses)
    raw_max = sum(r['max_points'] for r in responses)
    # Scale to 30 as requested for standard MMSE comparison
    scaled_score = (raw_score / raw_max) * 30 if raw_max > 0 else 0

    return sanitize_data({
        "total_score": scaled_score,
        "max_score": 30.0,
        "disease_prediction": prediction,
        "typing_summary": typing_summary,
        "responses": responses
    })

@app.get("/api/report/{session_id}")
async def get_report(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if "prediction" not in session:
        # Re-run prediction if not cached
        typing_summary = analyzer.aggregate_session_metrics(session["responses"])
        features = extractor.extract_features(session["responses"], typing_summary)
        session["prediction"] = predictor.predict(features)

    from fastapi.responses import StreamingResponse
    pdf_buffer = data_manager.generate_pdf_report(
        {"session_id": session_id},
        session["prediction"],
        session["responses"]
    )
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=MMSE_Report_{session_id}.pdf"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
