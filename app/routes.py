from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.future import select
import shortuuid
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession


from .database import get_db
from .schemas import URLCreate
from .crud import (
    get_url, create_url, delete_url, update_url, get_url_stats, search_url,
    update_project_name, get_links_by_project, fetch_popular_links,
    get_user_by_username, get_user, create_access_token, verify_password
)
from .utils import hash_password
from .models import URLModel, User


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/links", tags=["URL Shortener"])

# Настройка для работы с паролями и JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/links/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/register")
async def register_user(username: str, email: str, password: str, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_username(db, username=username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hash_password(password)

    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"User registered: {new_user.username}, Email: {new_user.email}")

    return new_user

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user(db, form_data.username)
    if not user or not await verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/shorten")
async def shorten_url(
        url_data: URLCreate,
        db: AsyncSession = Depends(get_db),
        expires_at: Optional[str] = None,
        project_name: Optional[str] = None
):
    """Создание короткой ссылки с возможностью указания времени жизни и проекта"""
    short_code = shortuuid.ShortUUID().random(length=6)
    custom_alias = url_data.custom_alias
    expires_at_datetime = None

    # Преобразование времени жизни ссылки, если оно задано
    if expires_at:
        try:
            expires_at_datetime = datetime.strptime(expires_at, "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD HH:MM.")

    # Проверка на уникальность custom_alias, если он указан
    if custom_alias:
        async with db.begin():
            result = await db.execute(select(URLModel).filter(URLModel.custom_alias == custom_alias))
            existing_alias = result.scalar_one_or_none()
            if existing_alias:
                raise HTTPException(status_code=400, detail="Custom alias already exists.")


    new_url = await create_url(db, short_code, url_data.url, custom_alias, expires_at_datetime, project_name)
    logger.info(f"Shortened URL created: {new_url.short_code} for {new_url.original_url}")

    return {
        "short_code": new_url.short_code,
        "original_url": new_url.original_url,
        "expires_at": new_url.expires_at,
        "project_name": new_url.project_name
    }

    await db.commit()


@router.delete("/{short_code}")
async def remove_url(short_code: str, db: AsyncSession = Depends(get_db)):
    """Удаление короткой связки короткой ссылки и url"""
    url_entry = await get_url(db, short_code)
    if url_entry is None:
        raise HTTPException(status_code=404, detail="URL not found")

    logger.info(f"Attempting to delete URL: {url_entry.short_code}")

    if not await delete_url(db, short_code):
        raise HTTPException(status_code=404, detail="URL not found")

    logger.info(f"Deleted URL: {url_entry.short_code}")

    FastAPICache.clear()

    return {"message": "URL deleted successfully"}


@router.put("/{short_code}")
async def modify_url(short_code: str, new_url: str, db: AsyncSession = Depends(get_db)):
    """К короткой ссылке привязывается новая длинная ссылка"""
    url_entry = await get_url(db, short_code)
    if url_entry is None:
        raise HTTPException(status_code=404, detail="URL not found")

    updated_url = await update_url(db, short_code, new_url)
    if not updated_url:
        raise HTTPException(status_code=404, detail="URL not found")

    FastAPICache.clear()

    return {
        "short_code": short_code,
        "original_url": updated_url.original_url,
        "expires_at": updated_url.expires_at
    }

@router.get("/{short_code}")
@cache(expire=60)  # Кэшируем ссылку на 60 секунд
async def retrieve_url(short_code: str, db: AsyncSession = Depends(get_db)):
    """Перенаправление на оригинальный URL по короткому коду"""
    url_entry = await get_url(db, short_code)
    if url_entry is None:
        raise HTTPException(status_code=404, detail="Link not found")

    # Обновляем количество переходов по ссылке и время последнего доступа
    url_entry.clicks += 1
    url_entry.last_accessed_at = datetime.utcnow()

    await db.commit()

    return {"message": "Redirect successful"}


@router.get("/search/")
async def search(original_url: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Поиск короткой ссылки по оригинальному URL"""
    url_entry = await search_url(db, original_url)
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")
    return {
        "short_code": url_entry.short_code,
        "original_url": url_entry.original_url,
        "expires_at": url_entry.expires_at
    }


@router.get("/popular_links/")
@cache(expire=3600)  # Кэшируем результат на 1 час
async def get_popular_links(db: AsyncSession = Depends(get_db)):
    """Получение 10 популярных ссылок"""
    popular_links = await fetch_popular_links(db)
    return {"popular_links": popular_links}


@router.get("/{short_code}/stats")
async def get_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    """Получение статистики по ссылке"""
    return await get_url_stats(db, short_code)


@router.put("/{short_code}/project")
async def modify_project(short_code: str, project_name: str, db: AsyncSession = Depends(get_db)):
    """Обновление названия проекта для ссылки"""
    db_url = await get_url(db, short_code=short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    updated_url = await update_project_name(db, short_code, project_name)
    if not updated_url:
        raise HTTPException(status_code=404, detail="URL not found")

    return {
        "short_code": short_code,
        "project_name": updated_url.project_name
    }


@router.get("/projects/{project_name}/links")
async def get_project_links(project_name: str, db: AsyncSession = Depends(get_db)):
    """Получение всех ссылок в проекте"""
    links = await get_links_by_project(db, project_name)
    if not links:
        raise HTTPException(status_code=404, detail="No links found for this project")
    return [{"short_code": link.short_code, "original_url": link.original_url, "expires_at": link.expires_at} for link in links]


