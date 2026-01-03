import pika
import os
from sqlmodel import Field, SQLModel
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncio  
from telebot import send_alert_message
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy.dialects.postgresql import JSONB
from metric_ingestion_models import DeviceMetric, DeviceMetricGroup as MetricGroupIncome 
from typing import List, Set


DB_URL = os.getenv("DATABASE_URL")

async_engine = create_async_engine(
    url = DB_URL,
    echo = True
)

class DeviceStatus(str, Enum):
    Normal = "normal"
    Warning = "warning"
    Critical = "critical"

class DeviceMetricGroup(SQLModel, table=True):
    __tablename__ = "alerts"
    id: UUID =  Field(default_factory=uuid4, primary_key=True)
    device_id: str = Field(default="default")
    status: DeviceStatus = Field(default=DeviceStatus.Normal) 
    metrics_raw: list = Field(default=[], sa_type=JSONB)
    
    @property
    def metrics(self) -> List[DeviceMetric]:
        return [DeviceMetric(**metric) if isinstance(metric, dict) else metric for metric in self.metrics_raw]
    
    @metrics.setter
    def metrics(self, metrics: List[DeviceMetric]):
        self.metrics_raw = metrics

    


async def initdb():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=async_engine, class_ = AsyncSession, expire_on_commit = False
    )

    async with async_session() as session:
        yield session

async def save_data(data: MetricGroupIncome, status: DeviceStatus):
    record = DeviceMetricGroup(device_id = data.device_id, status = status)

    record.metrics = data.metrics

    session = await get_session()

    session.add(record)

    await session.commit()

def process_message(payload):

    def check_status(metric: float)-> DeviceStatus:
        if metric >= 80:
            return DeviceStatus.Critical
        elif metric >= 61:
            return DeviceStatus.Warning
        else:
            return DeviceStatus.Normal
    def decide_overall_status(status_all: Set[DeviceStatus]) -> DeviceStatus:
        if DeviceStatus.Critical in status_all:
            return DeviceStatus.Critical
        elif DeviceStatus.Warning in status_all:
            return DeviceStatus.Warning
        return DeviceStatus.Normal
    metric_group: MetricGroupIncome = MetricGroupIncome.from_json(payload)

    status_set: Set[DeviceStatus] = set()
    msg = f"Device: <code>{metric_group.device_id}</code>\n"
    for metric in metric_group.metrics:
        st = check_status(metric.value)

        status_set.add(st)

        if st == DeviceStatus.Critical:
            msg += "".join(["🚨 <b>Alert System</b> 🚨\n",\
                            f"Metric: <b>{metric.name}</b>",\
                            f"Value: <b>{metric.value}%</b>\n",\
                            f"Status: <b>{st}</b>\n"])
    overall_status = decide_overall_status(status_set)

    if overall_status == DeviceStatus.Critical:
        send_alert_message(msg)
    
    asyncio.run(save_data(metric_group, overall_status))


if __name__ == "__main__":
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
