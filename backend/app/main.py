from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import router as api_router
from app.core.settings import settings
import uvicorn

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Document Quality & Blurriness Verification Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "base_url": settings.BASE_URL,
        "api_v1_url": settings.API_V1_URL,
        "docs_url": f"{settings.BASE_URL.rstrip('/')}/docs",
        "health_url": f"{settings.API_V1_URL}/health",
        "message": f"Welcome to {settings.PROJECT_NAME}. Visit /docs for API documentation."
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
