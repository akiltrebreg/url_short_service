from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging
from .models import URLModel
from .database import AsyncSessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

N_DAYS_UNUSED = 30  # Количество дней после последнего использования, чтобы удалить ссылку

# Функция для создания новой сессии БД
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session

# Задача для удаления устаревших ссылок
async def delete_expired_links():
    async for db in get_db_session():
        current_time = datetime.utcnow()
        async with db.begin():
            expired_links = await db.execute(
                select(URLModel).filter(URLModel.expires_at < current_time)
            )
            for link in expired_links.scalars():
                await db.delete(link)
                logger.info(f"Expired URL deleted: {link.short_code}")
        await db.commit()

# Задача для удаления неиспользуемых ссылок
async def delete_unused_links():
    async for db in get_db_session():
        threshold_date = datetime.utcnow() - timedelta(days=N_DAYS_UNUSED)
        async with db.begin():
            unused_links = await db.execute(
                select(URLModel).filter(
                    URLModel.last_used_at != None,  # Исключаем ссылки, по которым не было переходов
                    URLModel.last_used_at < threshold_date
                )
            )
            for link in unused_links.scalars():
                await db.delete(link)
                logger.info(f"Deleted unused URL: {link.short_code}")
        await db.commit()

# Запуск планировщика задач
scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.add_job(delete_expired_links, "interval", minutes=60)
    scheduler.add_job(delete_unused_links, "interval", hours=24)  # Раз в сутки
    scheduler.start()
