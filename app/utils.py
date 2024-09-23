#Вспомогательные функции, такие как хэширование паролей и валидация email. Эти функции помогают провести обработку данных перед сохранением их в базу данных или перед передачей клиенту.

from passlib.context import CryptContext
from email_validator import validate_email, EmailNotValidError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def validate_email_address(email: str) -> str:
    try:
        valid = validate_email(email)
        return valid.normalized
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email: {str(e)}")
