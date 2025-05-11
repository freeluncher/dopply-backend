from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)  # Added length for VARCHAR
    email = Column(String(100), unique=True, index=True, nullable=False)  # Added length for VARCHAR
    hashed_password = Column(String(255), nullable=False)  # Added length for VARCHAR
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
