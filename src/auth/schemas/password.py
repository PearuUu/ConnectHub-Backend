from pydantic import BaseModel, field_validator


class PasswordChange(BaseModel):
    password: str
    password_confirmation: str

    @field_validator("password")
    def password_must_be_valid(cls, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in password):
            raise ValueError(
                "Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            raise ValueError(
                "Password must contain at least one lowercase letter")
        if not any(char in "!@#$%^&*" for char in password):
            raise ValueError(
                "Password must contain at least one special character")
        return password

    @field_validator("password_confirmation")
    def password_confirmation_must_match(cls, password_confirmation, values):
        if "password" in values.data and password_confirmation != values.data["password"]:
            raise ValueError("Password confirmation must match password")
        return password_confirmation
    
    #TODO: Create schema with password and password_confirm,
    #Add current_password to PasswordChange, UserCreate inherits from new schema withhout current_password
