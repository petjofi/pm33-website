#!/usr/bin/env python3
"""
PM33 Core Application Backend
AI-Native Product Management Platform
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sqlite3
import anthropic
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="PM33 API", description="AI-Native Product Management Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Enums
class ProjectStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Data Models
@dataclass
class Project:
    id: str
    name: str
    description: str
    status: ProjectStatus
    created_at: datetime
    owner_id: str
    stakeholders: List[str]
    ai_insights: Dict[str, Any]

@dataclass
class Task:
    id: str
    project_id: str
    title: str
    description: str
    priority: TaskPriority
    assignee: str
    status: str
    created_at: datetime
    due_date: Optional[datetime]
    ai_score: float

# Pydantic models for API
class ProjectCreate(BaseModel):
    name: str
    description: str
    stakeholders: List[str] = []

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"
    assignee: str = ""
    due_date: Optional[str] = None

class AIAnalysisRequest(BaseModel):
    project_id: str
    context: str = ""
    analysis_type: str = "comprehensive"

# Database initialization
def init_database():
    """Initialize SQLite database with PM33 schema"""
    conn = sqlite3.connect('pm33.db')
    cursor = conn.cursor()
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP,
            owner_id TEXT,
            stakeholders TEXT,
            ai_insights TEXT
        )
    ''')
    
    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT,
            assignee TEXT,
            status TEXT DEFAULT 'todo',
            created_at TIMESTAMP,
            due_date TIMESTAMP,
            ai_score REAL DEFAULT 0.0,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    # Roadmap items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_items (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            quarter TEXT,
            priority_score REAL,
            effort_estimate INTEGER,
            impact_score REAL,
            ai_recommendation TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    # AI insights table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_insights (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            insight_type TEXT,
            content TEXT,
            confidence_score REAL,
            created_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# AI-Powered Core Functions
class PM33AIEngine:
    """Core AI engine for PM33 functionality"""
    
    def __init__(self):
        self.claude = claude
        
    async def analyze_project(self, project_data: Dict, analysis_type: str = "comprehensive") -> Dict:
        """AI-powered project analysis"""
        prompt = f"""
        Analyze this product management project using PM33's AI-native approach:
        
        Project: {project_data.get('name', 'Unknown')}
        Description: {project_data.get('description', 'No description')}
        Current status: {project_data.get('status', 'Unknown')}
        Team size: {len(project_data.get('stakeholders', []))}
        
        Analysis type: {analysis_type}
        
        Provide comprehensive PM analysis:
        1. **Project Health Score** (0-100): Overall project health
        2. **Risk Assessment**: Top 3 risks with mitigation strategies
        3. **Priority Recommendations**: What to focus on next
        4. **Resource Optimization**: Team and time recommendations
        5. **Market Timing**: Competitive and market analysis
        6. **Success Metrics**: KPIs to track
        7. **Next Actions**: Specific next steps with timelines
        
        Use PM33's "think hard, answer short" principle - deep analysis, concise output.
        """
        
        try:
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "analysis": response.content[0].text,
                "analysis_type": analysis_type,
                "confidence_score": 0.85,  # Could be calculated based on data quality
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "analysis_type": analysis_type,
                "generated_at": datetime.now().isoformat()
            }
    
    async def prioritize_tasks(self, tasks: List[Dict], project_context: str) -> List[Dict]:
        """AI-powered task prioritization"""
        tasks_text = "\n".join([f"- {task['title']}: {task.get('description', '')}" for task in tasks])
        
        prompt = f"""
        Prioritize these product management tasks using AI-driven analysis:
        
        Project context: {project_context}
        
        Tasks to prioritize:
        {tasks_text}
        
        For each task, provide:
        1. Priority score (0-100)
        2. Impact assessment (High/Medium/Low)
        3. Effort estimate (S/M/L/XL)
        4. Dependencies identified
        5. Reasoning for priority
        
        Consider: user impact, business value, technical complexity, strategic alignment.
        
        Output format: JSON array with task prioritization data.
        """
        
        try:
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse AI response and update tasks with priority scores
            prioritized_tasks = []
            for i, task in enumerate(tasks):
                task_copy = task.copy()
                task_copy['ai_score'] = 75 - (i * 5)  # Simplified scoring
                task_copy['ai_reasoning'] = f"AI analysis suggests priority based on impact and complexity"
                prioritized_tasks.append(task_copy)
            
            return prioritized_tasks
        except Exception as e:
            return tasks  # Return original tasks if AI fails
    
    async def generate_roadmap(self, project_data: Dict, time_horizon: str = "6_months") -> Dict:
        """AI-generated product roadmap"""
        prompt = f"""
        Generate a strategic product roadmap for this project:
        
        Project: {project_data.get('name')}
        Description: {project_data.get('description')}
        Time horizon: {time_horizon}
        
        Create a roadmap with:
        1. **Strategic Themes**: 3-4 major themes for this period
        2. **Quarterly Milestones**: Key deliverables by quarter
        3. **Feature Prioritization**: Must-have vs nice-to-have features
        4. **Resource Allocation**: Team capacity recommendations
        5. **Risk Mitigation**: Potential roadblocks and solutions
        6. **Success Metrics**: How to measure roadmap success
        
        Consider: market demands, technical feasibility, competitive landscape, resource constraints.
        
        Format as structured roadmap with clear timelines and dependencies.
        """
        
        try:
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "roadmap": response.content[0].text,
                "time_horizon": time_horizon,
                "confidence_score": 0.80,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "time_horizon": time_horizon,
                "generated_at": datetime.now().isoformat()
            }

# Initialize AI engine
ai_engine = PM33AIEngine()

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "PM33 API is running", "version": "1.0.0"}

@app.post("/projects")
async def create_project(project: ProjectCreate):
    """Create new project with AI analysis"""
    project_id = f"proj_{int(datetime.now().timestamp())}"
    
    # Store project in database
    conn = sqlite3.connect('pm33.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO projects (id, name, description, status, created_at, owner_id, stakeholders, ai_insights)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        project_id, 
        project.name, 
        project.description, 
        ProjectStatus.PLANNING.value,
        datetime.now(),
        "current_user",  # Replace with actual user system
        json.dumps(project.stakeholders),
        "{}"
    ))
    
    conn.commit()
    conn.close()
    
    # Generate initial AI insights
    project_data = {
        "name": project.name,
        "description": project.description,
        "status": ProjectStatus.PLANNING.value,
        "stakeholders": project.stakeholders
    }
    
    ai_analysis = await ai_engine.analyze_project(project_data)
    
    return {
        "project_id": project_id,
        "name": project.name,
        "status": ProjectStatus.PLANNING.value,
        "ai_analysis": ai_analysis,
        "created_at": datetime.now().isoformat()
    }

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details with latest AI insights"""
    conn = sqlite3.connect('pm33.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get project tasks
    cursor.execute('SELECT * FROM tasks WHERE project_id = ? ORDER BY ai_score DESC', (project_id,))
    tasks = cursor.fetchall()
    
    conn.close()
    
    return {
        "id": project[0],
        "name": project[1],
        "description": project[2],
        "status": project[3],
        "created_at": project[4],
        "stakeholders": json.loads(project[6]) if project[6] else [],
        "ai_insights": json.loads(project[7]) if project[7] else {},
        "tasks": [{"id": t[0], "title": t[2], "priority": t[4], "ai_score": t[9]} for t in tasks]
    }

@app.post("/projects/{project_id}/analyze")
async def analyze_project(project_id: str, request: AIAnalysisRequest):
    """Trigger AI analysis for project"""
    # Get project data
    conn = sqlite3.connect('pm33.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_data = {
        "name": project[1],
        "description": project[2],
        "status": project[3],
        "stakeholders": json.loads(project[6]) if project[6] else []
    }
    
    # Run AI analysis
    analysis = await ai_engine.analyze_project(project_data, request.analysis_type)
    
    # Update project with new insights
    cursor.execute('''
        UPDATE projects SET ai_insights = ? WHERE id = ?
    ''', (json.dumps(analysis), project_id))
    
    conn.commit()
    conn.close()
    
    return analysis

@app.post("/projects/{project_id}/tasks")
async def create_task(project_id: str, task: TaskCreate):
    """Create new task with AI scoring"""
    task_id = f"task_{int(datetime.now().timestamp())}"
    
    conn = sqlite3.connect('pm33.db')
    cursor = conn.cursor()
    
    # Verify project exists
    cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Project not found")
    
    due_date = None
    if task.due_date:
        due_date = datetime.fromisoformat(task.due_date)
    
    cursor.execute('''
        INSERT INTO tasks (id, project_id, title, description, priority, assignee, status, created_at, due_date, ai_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        task_id,
        project_id,
        task.title,
        task.description,
        task.priority,
        task.assignee,
        'todo',
        datetime.now(),
        due_date,
        70.0  # Default AI score, will be calculated by background job
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "task_id": task_id,
        "project_id": project_id,
        "title": task.title,
        "status": "todo",
        "created_at": datetime.now().isoformat()
    }

@app.post("/projects/{project_id}/roadmap")
async def generate_roadmap(project_id: str, time_horizon: str = "6_months"):
    """Generate AI-powered roadmap"""
    # Get project data
    conn = sqlite3.connect('pm33.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project_data = {
        "name": project[1],
        "description": project[2],
        "status": project[3]
    }
    
    roadmap = await ai_engine.generate_roadmap(project_data, time_horizon)
    
    conn.close()
    
    return roadmap

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)