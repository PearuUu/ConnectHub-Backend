from pydantic import BaseModel, field_validator


class PasswordBase(BaseModel):
    password: str
    password_confirmation: str

    @staticmethod
    def validate_password(password: str) -> str:
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

    @field_validator("password")
    def password_must_be_valid(cls, password):
        return cls.validate_password(password)

    @field_validator("password_confirmation")
    def password_confirmation_must_match(cls, password_confirmation, values):
        if "password" in values.data and password_confirmation != values.data["password"]:
            raise ValueError("Password confirmation must match password")
        return password_confirmation


class PasswordChange(PasswordBase):
    current_password: str

    @field_validator("current_password")
    def current_password_must_be_valid(cls, current_password):
        return PasswordBase.validate_password(current_password)


class Password(PasswordBase):
    pass
