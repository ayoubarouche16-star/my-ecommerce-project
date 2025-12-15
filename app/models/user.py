from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from passlib.hash import bcrypt
from app.database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

    # set password (hash)
    def set_password(self, password: str):
        self.password_hash = bcrypt.hash(password)

    # check password
    def check_password(self, password: str) -> bool:
        try:
            return bcrypt.verify(password, self.password_hash)
        except Exception:
            return False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
from passlib.hash import bcrypt
from datetime import datetime

class User:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = bcrypt.hash(password)
        self.created_at = datetime.utcnow()

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)
from passlib.hash import bcrypt
from app.database.db import get_db_connection

class User:
    @staticmethod
    def create(username, password):
        hashed = bcrypt.hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()

    @staticmethod
    def find_by_username(username):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def verify_password(password, hashed):
        return bcrypt.verify(password, hashed)
# app/models/user.py
from passlib.hash import bcrypt
from app.database.db import get_db_connection

class User:
    @staticmethod
    def create(username: str, password: str):
        hashed = bcrypt.hash(password)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        conn.commit()
        uid = cur.lastrowid
        conn.close()
        return uid

    @staticmethod
    def find_by_username(username: str):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        return row

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        try:
            return bcrypt.verify(password, hashed)
        except Exception:
            return False
from app.database.db import get_connection
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
        (username, hash_password(password), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user
