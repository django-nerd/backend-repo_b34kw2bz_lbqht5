"""
Database Schemas for Sports Coaching App

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class Athlete(BaseModel):
    """
    Athletes collection schema
    Collection: "athlete"
    """
    first_name: str = Field(..., description="Athlete first name")
    last_name: str = Field(..., description="Athlete last name")
    sport: Optional[str] = Field(None, description="Primary sport")
    team: Optional[str] = Field(None, description="Team or group")
    age: Optional[int] = Field(None, ge=0, le=120)
    tags: List[str] = Field(default_factory=list, description="Labels like positions, strengths")

class Note(BaseModel):
    """
    Notes collection schema
    Collection: "note"
    """
    athlete_id: str = Field(..., description="Related athlete document _id as string")
    title: str = Field(..., description="Short note title")
    content: str = Field(..., description="Detailed observation / coaching note")
    focus_skills: List[str] = Field(default_factory=list, description="Skills or areas of focus")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Optional 1-5 rating")

class SkillPlan(BaseModel):
    """
    Skill plans collection schema
    Collection: "skillplan"
    """
    athlete_id: str = Field(...)
    skill: str = Field(..., description="Skill to develop")
    goal: str = Field(..., description="Specific measurable goal")
    timeframe_weeks: Optional[int] = Field(None, ge=1, le=52)
    notes: Optional[str] = Field(None)
