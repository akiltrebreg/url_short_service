from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from fastapi import HTTPException, status, Depends
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .models import URLModel, User
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .database import get_db

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def get_url(db: AsyncSession, short_code: str):
    """Получение URL по короткому коду без обновления статистики"""
    async with db.begin():
        result = await db.execute(select(URLModel).filter(URLModel.short_code == short_code))
        url_entry = result.scalar_one_or_none()

        if url_entry is None:
            logger.error(f"URL entry not found for short_code: {short_code}")
            raise HTTPException(status_code=404, detail="URL not found")

        if url_entry.expires_at and url_entry.expires_at < datetime.utcnow():
            await delete_url(db, short_code)
            raise HTTPException(status_code=410, detail="Link expired")

    return url_entry

async def create_url(
        db: AsyncSession,
        short_code: str,
        original_url: str,
        custom_alias: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        project_name: Optional[str] = None
):
    """Создание нового URL с кастомным алиасом, сроком действия и привязкой к проекту"""
    new_url = URLModel(
        short_code=short_code,
        original_url=original_url,
        custom_alias=custom_alias,
        expires_at=expires_at,
        project_name=project_name,
        last_accessed_at=datetime.utcnow(),
        clicks=0
    )

    async with db.begin():
        db.add(new_url)
        await db.commit()
        return new_url

async def delete_url(db: AsyncSession, short_code: str):
    """Удаление URL по короткому коду"""
    async with db.begin():
        result = await db.execute(select(URLModel).filter(URLModel.short_code == short_code))
        url_entry = result.scalar_one_or_none()

        if url_entry:
            await db.delete(url_entry)
            await db.commit()
            return True

    return False

async def update_url(db: AsyncSession, short_code: str, new_url: str):
    """Обновление оригинального URL по короткому коду"""
    async with db.begin():
        result = await db.execute(select(URLModel).filter(URLModel.short_code == short_code))
        url_entry = result.scalar_one_or_none()

        if url_entry:
            url_entry.original_url = new_url
            await db.commit()

    if url_entry:
        await db.refresh(url_entry)

    return url_entry

async def get_url_stats(db: AsyncSession, short_code: str):
    """Получение статистики по короткому коду"""
    async with db.begin():
        result = await db.execute(select(URLModel).filter(URLModel.short_code == short_code))
        url_entry = result.scalar_one_or_none()

        if not url_entry:
            logger.error(f"URL entry not found for short_code: {short_code}")
            raise HTTPException(status_code=404, detail="URL not found")

        return {
            "short_code": url_entry.short_code,
            "original_url": url_entry.original_url,
            "created_at": url_entry.created_at.isoformat(),
            "clicks": url_entry.clicks,
            "last_accessed_at": url_entry.last_accessed_at.isoformat() if url_entry.last_accessed_at else None
        }

async def search_url(db: AsyncSession, original_url: str):
    """Поиск ссылки по оригинальному URL"""
    async with db.begin():
        result = await db.execute(select(URLModel).filter(URLModel.original_url == original_url))
        return result.scalar_one_or_none()

async def update_project_name(db: AsyncSession, short_code: str, project_name: str):
    """Обновление проекта"""
    async with db.begin():
        result = await db.execute(select(URLModel).filter(URLModel.short_code == short_code))
        url_entry = result.scalar_one_or_none()

        if not url_entry:
            return None

        url_entry.project_name = project_name
        await db.commit()
        return url_entry

async def get_links_by_project(db: AsyncSession, project_name: str):
    """Получение ссылок по проекту"""
    async with db.begin():
        result = await db.execute(select(URLModel).filter(URLModel.project_name == project_name))
        return result.scalars().all()

async def delete_unused_links(db: AsyncSession, days: int = 10):
    """Удаляет ссылки, которые не использовались более N дней"""
    threshold_date = datetime.utcnow() - timedelta(days=days)
    async with db.begin():
        await db.execute(
            delete(URLModel).where(URLModel.last_accessed_at < threshold_date)
        )
        await db.commit()

async def fetch_popular_links(db: AsyncSession):
    """Получение 10 популярных ссылок"""
    async with db.begin():
        result = await db.execute(
            select(URLModel)
            .order_by(URLModel.clicks.desc().nulls_last())
            .limit(10)
        )
        popular_links = result.scalars().all()
        return popular_links

async def get_user_by_username(db: AsyncSession, username: str):
    """Функция для получения пользователя из базы данных по имени пользователя"""
    async with db.begin():
        result = await db.execute(select(User).filter(User.username == username))

        return result.scalar_one_or_none()


# Функции работы с пользователями
async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()

# Создаем экземпляр CryptContext для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/links/token")

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Функции работы с токенами
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Функция, которая получает текущего пользователя из токена
def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user