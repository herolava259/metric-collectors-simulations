import pika
import json
import os
from sqlmodel import Field, SQLModel
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncio  
from telebot import send_alert_message
from uuid import UUID, uuid4
from enum import Enum
DB_URL = os.getenv("DATABASE_URL")

async_engine = create_async_engine(
    url = DB_URL,
    echo = True
)

class DeviceStatus(str, Enum):
    Normal = "normal"
    Warning = "warning"
    Critical = "critical"

class DeviceMetric(SQLModel, table=True):
    __tablename__ = "alerts"
    id: UUID =  Field(default_factory=uuid4, primary_key=True)
    device_id: str = Field(default="default")
    status: DeviceStatus = Field(default=DeviceStatus.Normal) 
    metrics: str = Field(default="{}")

async def initdb():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=async_engine, class_ = AsyncSession, expire_on_commit = False
    )

    async with async_session() as session:
        yield session

async def save_data(data: dict):
    record = DeviceMetric(**data)

    session = await get_session()

    session.add(record)

    await session.commit()

def process_message(body):
    data = json.loads(body)
    metrics = data['metrics']
    device_id = data['device_id']
    cpu_usage = data["cpu_usage"]
    
    # ex alert with cpu_usage
    if metrics["cpu_usage"] >= 80:
        status = "critical"
        msg = (
            f"🚨 <b>Alert System</b> 🚨\n"
            f"Device: <code>{device_id}</code>\n"
            f"Info: {data['metric']}\n"
            f"Value: <b>{cpu_usage}%</b>\n"
            f"Status: {status}"
        )
        
        asyncio.run(send_alert_message(''.join(msg)))
    elif metrics["cpu_usage"] >= 60:
        status = "warning"
    else:
        status = "normal"
    
    body["status"] = status
    asyncio.run(save_data(body))


asyncio.run(initdb())

R_URL = os.getenv("RABBITMQ_URL")
params = pika.URLParameters(R_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.exchange_declare(exchange="metrics", exchange_type="fanout")

result = channel.queue_declare(queue='metrics_queue', durable=True, exclusive = True)

queue_name = result.method.queue

channel.queue_bind(exchange="metrics", queue=queue_name)
channel.basic_consume(queue=queue_name, on_message_callback=process_message, auto_ack=True)

print("Worker is waiting for messages...")
channel.start_consuming()