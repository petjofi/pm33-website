from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import strategic_chat

app = FastAPI(
    title="PM33 Strategic AI Co-Pilot API",
    description="AI-native product management platform that transforms PMs into PMOs through agentic AI teams",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include strategic chat routes
app.include_router(strategic_chat.router)

@app.get("/")
async def root():
    return {
        "message": "PM33 Strategic AI Co-Pilot API",
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pm33-api"}