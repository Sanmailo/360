from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import HTTPException, status
import os
from passlib.context import CryptContext

# Load environment variables
load_dotenv()

# Fetch the secret key from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Validate that the secret key is loaded correctly
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY environment variable is not set.")

# Password context setup for hashing and verifying passwords
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    # Sign the JWT with the SECRET_KEY and ALGORITHM
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    """Verify and decode a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_cxt.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_cxt.hash(password)

def create_reset_token(email: str, expires_delta: timedelta = timedelta(minutes=15)):
    """Create a reset token for password reset."""
    data = {"sub": email}
    return create_access_token(data, expires_delta)
