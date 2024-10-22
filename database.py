from pymongo import MongoClient
from dotenv import load_dotenv
import os
from typing import Optional
from fastapi import HTTPException
from security import create_access_token, verify_password

# Load environment variables from .env file
load_dotenv()

# MongoDB connection setup with error handling
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["callpoint"]
    users_collection = db["users"]
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    raise HTTPException(status_code=500, detail="Database connection failed")

def connect_db():
    """Check connection to the MongoDB database."""
    try:
        # Ping the server to check if it's connected
        client.admin.command('ping')
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def get_user_by_email(email: str):
    """Retrieve a user from the database by their email."""
    try:
        user = users_collection.find_one({"email": email})
        return user  # Return None if not found
    except Exception as e:
        print(f"Error finding user by email: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving user")

def authenticate_user(email: Optional[str], phone_number: Optional[str], password: str):
    """
    Authenticate a user using either their email or phone number.
    
    Args:
        email (str): The email of the user.
        phone_number (str): The phone number of the user.
        password (str): The password provided by the user.

    Returns:
        dict: The user data if authentication is successful, None otherwise.
    """
    try:
        user = None

        # Check if the user exists using email
        if email:
            user = get_user_by_email(email)

        # If the user wasn't found by email, check by phone number
        if not user and phone_number:
            user = users_collection.find_one({"phoneNumber": phone_number})

        # Verify the password if the user exists
        if user and verify_password(password, user["password"]):
            return user
        
        return None  # Explicitly return None if authentication fails
    except Exception as e:
        print(f"Error authenticating user: {e}")
        raise HTTPException(status_code=500, detail="Error authenticating user")
