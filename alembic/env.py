import asyncio
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

config = context.config
target_metadata = Base.metadata

async def run_migrations_online():
    # Создаем асинхронный движок
    connectable = create_async_engine(config.get_main_option("sqlalchemy.url"), echo=True)

    # Создаем соединение с асинхронным движком
    async with connectable.connect() as connection:
        # Синхронно выполняем миграции
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

# Для выполнения асинхронных миграций
if context.is_offline_mode():
    print("Офлайн-режим не поддерживает асинхронные миграции.")
else:
    asyncio.run(run_migrations_online())
