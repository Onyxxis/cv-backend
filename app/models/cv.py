from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date, datetime

# Personal Information
class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    birthdate: Optional[date] = None
    gender: str
    email: EmailStr
    phone: str
    nationality: Optional[str] = None
    job_title: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None  
    

# Experience
class Experience(BaseModel):
    position: str
    company: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

# Education
class Education(BaseModel):
    degree_name: str
    institution: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None

# Skill
class Skill(BaseModel):
    name: str

# Project
class Project(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

# Language
class Language(BaseModel):
    name: str
    level: str  

# Certification
class Certification(BaseModel):
    title: str
    organization: str
    date_obtained: Optional[date] = None
    url: Optional[str] = None

# Main CV model
class CV(BaseModel):
    user_id: str
    template_id: Optional[str] = None
    title: str
    personal_info: PersonalInfo
    experiences: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []
    projects: List[Project] = []
    languages: List[Language] = []
    certifications: List[Certification] = []
    is_completed: bool = False   
    completion_percentage: int = 0 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# pour l'extraction de données
class ExtractedCVData(BaseModel):
    personal_info: PersonalInfo
    experiences: List[Experience] = []
    education: List[Education] = []
    skills: List[Skill] = []
    projects: List[Project] = []
    languages: List[Language] = []
    certifications: List[Certification] = []
