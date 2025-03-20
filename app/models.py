from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import validates, relationship
from datetime import datetime
from .database import Base
from typing import Optional
from pydantic import BaseModel


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True) # ID пользователя
    username = Column(String, unique=True, index=True, nullable=False) # Логин
    email = Column(String, unique=True, index=True, nullable=False) # Почта
    hashed_password = Column(String, nullable=False) # Захэшированный пароль
    created_at = Column(DateTime, default=datetime.utcnow) # Дата создания

    # Валидация username
    @validates('username')
    def validate_username(self, key, value):
        if len(value) < 3 or len(value) > 30:
            raise ValueError('Username must be between 3 and 30 characters.')
        return value

    # Валидация email
    @validates('email')
    def validate_email(self, key, value):
        if '@' not in value:
            raise ValueError('Invalid email address.')
        return value

    # Обратная связь с URLModel
    links = relationship("URLModel", back_populates="owner")


class URLModel(Base):
    __tablename__ = "shortened_urls"

    id = Column(Integer, primary_key=True, index=True) # ID ссылки
    short_code = Column(String, unique=True, index=True) # Короткая ссылка
    original_url = Column(String, index=True, nullable=False) # Оригинальный URL
    custom_alias = Column(String, unique=True, nullable=True)  # Кастомный alias
    created_at = Column(DateTime, default=datetime.utcnow) # Дата создания ссылки
    expires_at = Column(DateTime, nullable=True)  # Время истечения срока жизни ссылки
    clicks = Column(Integer, default=0, index=True)  # Количество переходов
    last_accessed_at = Column(DateTime, nullable=True)  # Последнее использование
    project_name = Column(String, nullable=True) # Наименование проекта
    owner_id = Column(Integer, ForeignKey("users.id"))  # Привязка к пользователю

    # Обратная связь с пользователем
    owner = relationship("User", back_populates="links")

    # Валидация custom_alias
    @validates('custom_alias')
    def validate_custom_alias(self, key, value):
        if value and (len(value) < 3 or len(value) > 30):
            raise ValueError('Alias must be between 3 and 30 characters.')
        return value


class TokenRequest(BaseModel):
    token: Optional[str] = None