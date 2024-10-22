from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from database import connect_db
from pydantic import BaseModel, EmailStr

# Create FastAPI instance
app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; consider specifying domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods; specify as needed
    allow_headers=["*"],  # Allow all headers; specify as needed
)

# Connect to database
connect_db()

# Include Auth routes
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Pydantic model example (optional)
class MessageResponse(BaseModel):
    message: str

@app.get("/", response_model=MessageResponse)
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}

# Running the application with Uvicorn
# Uncomment the following lines if you want to run the app directly
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
