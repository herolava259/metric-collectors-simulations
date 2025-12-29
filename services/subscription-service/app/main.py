from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, SQLModel, select
from typing import AsyncGenerator
from uuid import UUID, uuid4
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import sqlalchemy.dialects.sqlite
from datetime import datetime

from pydantic import BaseModel as DtoModel, Field as DtoField
from enum import Enum 

class SubscriptionStatus(str, Enum):
    pending = "pending"
    active = "active"
    cancelled = "cancelled"

class Subscription(SQLModel, table=True):
    id: UUID =  Field(default_factory=uuid4, primary_key=True)
    customer_name: str = Field(default="Home Basic", max_length=1024)
    phone_number: str = Field(default="0000000000")
    package_id: UUID = Field(default_factory=uuid4)
    start_date: float = Field(default_factory=lambda : datetime.now().timestamp(), )
    status: SubscriptionStatus = Field(default =SubscriptionStatus.pending)
    

sqlite_file_name = "database.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"



async_engine = create_async_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})

async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(bind = async_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on start up
    await create_db_and_tables()
    yield
    # on shutdown 

class CreateSubscriptionRequest(DtoModel):
    name: str = DtoField(default="Home Basic", max_length=1024)
    speed_mbps: int =DtoField(default=50, ge=30, le=200)
    price_per_month: int = DtoField(default=50_000, ge=45_000, le=10_000_000)
    description: str = DtoField(default="default-description", )
    active: bool = DtoField(default=True)

    

class UpdateSubscriptionRequest(Subscription):
    pass

class SubscriptionDto(Subscription):
    pass

app = FastAPI(lifespan=lifespan, title="subscription-api") 

@app.post("/create", response_model=SubscriptionDto)
async def create_package(req: CreateSubscriptionRequest, session: AsyncSession = Depends(get_session)):
    subscription = Subscription(**req.model_dump())

    subscription = Subscription.model_validate(subscription)

    session.add(subscription)

    await session.commit()

    await session.refresh(subscription)
    return SubscriptionDto(**subscription.model_dump())

@app.get("/get/{subscription_id}", response_model=SubscriptionDto)
async def get_by_id(subscription_id: UUID, session: AsyncSession = Depends(get_session)):

    query = select(SubscriptionDto).where(SubscriptionDto.id==subscription_id)

    result = await session.execute(query)

    row = result.one()

    if not row:
        raise HTTPException(status_code=404, detail="Package not found")
    
    
    return SubscriptionDto(**Subscription(**row._mapping).model_dump())


@app.put("/update/{package_id}", response_model=SubscriptionDto)
async def update(package_id: UUID, update_req: UpdateSubscriptionRequest,  session: AsyncSession = Depends(get_session)):
    query = select(Subscription).where(Subscription.id==package_id)

    row = (await session.execute(query)).one()


    if not row:
        raise HTTPException(status_code=404, detail="Package not found")
    
    record =  Subscription(**row._mapping)
    record.sqlmodel_update(update_req.model_dump())

    session.add(record)

    await session.commit()

    await session.refresh()

    return SubscriptionDto(**record.model_dump())


@app.patch("/update/partial/{package_id}", response_model=SubscriptionDto)
async def partial_update(package_id: UUID, update_req: UpdateSubscriptionRequest,  session: AsyncSession = Depends(get_session)):
    query = select(Subscription).where(Subscription.id==package_id)

    row = (await session.execute(query)).one()

    if not row:
        raise HTTPException(status_code=404, detail="Subscription not found")
    record = Subscription(**row._mapping)
    record.sqlmodel_update(update_req.model_dump(exclude_unset=True))

    session.add(record)

    await session.commit()

    await session.refresh()

    return SubscriptionDto(**record.model_dump())

@app.delete("/delete/{subscription_id}")
async def delete(subscription_id: UUID,  session: AsyncSession = Depends(get_session)):
    query = select().where(Subscription.id==subscription_id)

    row = (await session.execute(query)).one()

    if not row:
        raise HTTPException(status_code=404, detail="Subscription not found")
    

    session.delete(row)
    await session.commit()

    return {"ok": True}