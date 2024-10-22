from fastapi import FastAPI, APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from passlib.context import CryptContext
from models import SignUp, SignIn, User, ResetPasswordRequest, ResetPasswordForm, Token, PaystackPayment
from database import get_user_by_email, users_collection, authenticate_user
from security import create_access_token, verify_password, verify_access_token, create_reset_token
from jose import JWTError, jwt
from typing import Optional
from datetime import timedelta
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI()
router = APIRouter()

# Environment variables
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

# Authentication schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
bearer_scheme = HTTPBearer()

# Password context
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")
@router.post("/auth/token", response_model=Token)
async def sign_in_for_access_token(email: Optional[str] = None, phoneNumber: Optional[str] = None, password: str = Body(...)):
    user = authenticate_user(email, phoneNumber, password)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email/phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Remove 'await' if create_access_token is not async
    access_token = create_access_token(
        data={"sub": user["email"] if user["email"] else user["phoneNumber"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# SignUp route
@router.post("/SignUp")
async def sign_up_user(user: SignUp):
    # Ensure the 'confirmPassword' attribute is being accessed correctly
    if user.password != user.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    hashed_password = pwd_cxt.hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    del user_data["confirmPassword"]  # Remove 'confirmPassword' before storing the user data
    users_collection.insert_one(user_data)
    
    return {"message": "User signed up successfully"}


# SignIn route
@router.post("/SignIn", response_model=Token)
async def sign_in_user(form_data: SignIn):
    user = authenticate_user(form_data.email, form_data.phoneNumber, form_data.password)
    if not user or not verify_password(form_data.password, user["password"]):  
        raise HTTPException(status_code=401, detail="Invalid email/phone number or password")

    access_token_expires = timedelta(minutes=30)
    
    # Remove 'await' if create_access_token is not async
    access_token = create_access_token(
        data={"sub": user["email"] if user["email"] else user["phoneNumber"]}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# Reset password routes
@router.post("/auth/forget_password")
async def forget_password(request: ResetPasswordRequest):
    user = get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    reset_token = create_reset_token(request.email)
    return {"message": "Password reset token sent successfully", "reset_token": reset_token}

@router.post("/auth/reset_password")
async def reset_password(form_data: ResetPasswordForm):
    user = get_user_by_email(form_data.token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    hashed_password = pwd_cxt.hash(form_data.new_password)
    users_collection.update_one({"email": form_data.token}, {"$set": {"password": hashed_password}})
    
    return {"message": "Password has been reset successfully"}

# Paystack payment route
@router.post("/paystack/pay")
async def paystack_payment(payment: PaystackPayment):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": payment.email,
        "amount": payment.amount * 100  # Paystack expects amount in kobo (1 NGN = 100 kobo)
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return response.json()

# Include the router in the FastAPI application
app.include_router(router)
