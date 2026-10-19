from fastapi.security import OAuth2PasswordBearer

from dados.database import SessionLocal

# Esquema OAuth2 (Password Flow). Será usado pelo get_current_user.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()