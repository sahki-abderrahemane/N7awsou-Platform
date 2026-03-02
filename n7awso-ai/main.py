from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import logging
from routers import assistance_bot, planing_bot, email_marketing_automation
from routers import recommendation_system
import os
from dotenv import load_dotenv

print("Working directory:", os.getcwd())

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Tourism Assistant API starting up...")
    
    # Initialize recommendation system
    try:
        logger.info("Initializing recommendation system...")
        await recommendation_system.initialize_recommendation_system()
        logger.info("Recommendation system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize recommendation system: {e}")
        # Don't fail startup, just log the error
    
    yield
    
    # Shutdown
    logger.info("Tourism Assistant API shutting down...")
    
    # Cleanup assistant resources
    if hasattr(assistance_bot, 'assistant') and assistance_bot.assistant:
        await assistance_bot.assistant.cleanup()
    
    # Cleanup recommendation system
    try:
        await recommendation_system.prisma.disconnect()
        logger.info("Recommendation system disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting recommendation system: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Tourism Assistant API",
    description="AI-powered tourism assistant with chat memory and real-time communication",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://n7awsou-platform.vercel.app/"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Tourism Assistant API is running", "status": "healthy"}

# Include routers
app.include_router(assistance_bot.router, prefix="/api/v1", tags=["assistance"])
app.include_router(planing_bot.router, prefix="/chatbot/plan", tags=["planning"])
app.include_router(recommendation_system.router, prefix="/recommend", tags=["recommendation"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
