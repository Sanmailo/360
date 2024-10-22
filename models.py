from pydantic import BaseModel, EmailStr
from typing import Optional

# User model
class User(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    disabled: Optional[bool] = None

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# SignUp model
class SignUp(BaseModel):
    firstName: str
    middleName: Optional[str] = None
    lastName: str
    email: EmailStr
    phoneNumber: str
    sex: str
    password: str
    confirmPassword: str

# SignIn model
class SignIn(BaseModel):
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None  # Ensure this line is present
    password: str

# Reset Password Request
class ResetPasswordRequest(BaseModel):
    email: EmailStr

# Reset Password Form
class ResetPasswordForm(BaseModel):
    token: str
    new_password: str

# Paystack Payment model
class PaystackPayment(BaseModel):
    email: EmailStr
    amount: int
