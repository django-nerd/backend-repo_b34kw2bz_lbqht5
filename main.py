import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Athlete, Note, SkillPlan

app = FastAPI(title="Sports Coaching Notes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers

def to_str_id(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id")) if doc.get("_id") else None
    return doc

# Basic routes

@app.get("/")
def read_root():
    return {"message": "Sports Coaching Notes API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# Schemas endpoint for viewer
@app.get("/schema")
def get_schema():
    return {
        "athlete": Athlete.model_json_schema(),
        "note": Note.model_json_schema(),
        "skillplan": SkillPlan.model_json_schema(),
    }

# Athlete endpoints

class AthleteCreate(Athlete):
    pass

@app.post("/api/athletes")
def create_athlete(payload: AthleteCreate):
    athlete_id = create_document("athlete", payload)
    return {"id": athlete_id}

@app.get("/api/athletes")
def list_athletes(q: Optional[str] = None, tag: Optional[str] = None, limit: int = 50):
    filter_dict = {}
    if tag:
        filter_dict["tags"] = {"$in": [tag]}
    docs = get_documents("athlete", filter_dict, limit)
    # basic search in memory over small result set
    if q:
        ql = q.lower()
        docs = [d for d in docs if ql in (d.get("first_name","")+" "+d.get("last_name","")) .lower() or ql in (d.get("sport","") or "").lower()]
    return [to_str_id(d) for d in docs]

# Notes endpoints

class NoteCreate(Note):
    pass

@app.post("/api/notes")
def create_note(payload: NoteCreate):
    # ensure athlete exists
    try:
        _ = ObjectId(payload.athlete_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid athlete_id")
    note_id = create_document("note", payload)
    return {"id": note_id}

@app.get("/api/notes")
def list_notes(athlete_id: Optional[str] = None, limit: int = 100):
    filter_dict = {"athlete_id": athlete_id} if athlete_id else {}
    docs = get_documents("note", filter_dict, limit)
    return [to_str_id(d) for d in docs]

# Skill Plans

class SkillPlanCreate(SkillPlan):
    pass

@app.post("/api/skill-plans")
def create_skill_plan(payload: SkillPlanCreate):
    # ensure athlete id format only
    try:
        _ = ObjectId(payload.athlete_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid athlete_id")
    plan_id = create_document("skillplan", payload)
    return {"id": plan_id}

@app.get("/api/skill-plans")
def list_skill_plans(athlete_id: Optional[str] = None, limit: int = 100):
    filter_dict = {"athlete_id": athlete_id} if athlete_id else {}
    docs = get_documents("skillplan", filter_dict, limit)
    return [to_str_id(d) for d in docs]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
