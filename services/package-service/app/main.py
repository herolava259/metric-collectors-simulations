from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, SQLModel, Session, select
from typing import Annotated, AsyncGenerator, Optional
from uuid import UUID, uuid4
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import aiosqlite

from pydantic import BaseModel as DtoModel, Field as DtoField

class Package(SQLModel, table=True):
    id: UUID =  Field(default_factory=uuid4, primary_key=True)
    name: str = Field(default="Home Basic", max_length=1024)
    speed_mbps: int = Field(default=50, ge=30, le=200)
    price_per_month: int = Field(default=50_000, ge=45_000, le=10_000_000)
    description: str = Field(default="default-description", )
    active: bool = Field(default=True)


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


#####
## Request-Response models
####

class CreatePackageRequest(DtoModel):
    name: str = DtoField(default="Home Basic", max_length=1024)
    speed_mbps: int =DtoField(default=50, ge=30, le=200)
    price_per_month: int = DtoField(default=50_000, ge=45_000, le=10_000_000)
    description: str = DtoField(default="default-description", )
    active: bool = DtoField(default=True)

class CreatePackageResponse(DtoModel):
    id: Optional[UUID] = DtoField(default = None)
    name: str = DtoField(default="Home Basic", max_length=1024)
    speed_mbps: int =DtoField(default=50, ge=30, le=200)
    price_per_month: int = DtoField(default=50_000, ge=45_000, le=10_000_000)
    description: str = DtoField(default="default-description", )
    active: bool = DtoField(default=True)

class UpdatePackageRequest(Package):
    pass

class PackageDto(Package):
    pass


app = FastAPI(lifespan=lifespan, title="package-api") 


@app.post("/create", response_model=CreatePackageResponse)
async def create_package(req: CreatePackageRequest, session: AsyncSession = Depends(get_session)):
    package = Package(**req.model_dump())

    package = Package.model_validate(package)

    session.add(package)

    await session.commit()

    await session.refresh(package)
    return CreatePackageResponse(**package.model_dump())

@app.get("/get/{package_id}", response_model=PackageDto)
async def get_by_id(package_id: UUID, session: AsyncSession = Depends(get_session)):

    query = select(Package).where(Package.id==package_id)

    result = await session.execute(query)

    row = result.one()

    if not row:
        raise HTTPException(status_code=404, detail="Package not found")
    
    
    return PackageDto(**Package(**row._mapping).model_dump())


@app.put("/update/{package_id}", response_model=PackageDto)
async def update(package_id: UUID, update_req: UpdatePackageRequest,  session: AsyncSession = Depends(get_session)):
    print("-------------***********&&&&&&&&&", package_id)
    query = select(Package).where(Package.id==package_id)

    row = (await session.execute(query)).one()


    if not row:
        raise HTTPException(status_code=404, detail="Package not found")
    print("pass exist ******************************************************")
    record =  Package(**row._mapping)
    record.sqlmodel_update(update_req.model_dump())

    session.add(record)

    await session.commit()

    await session.refresh()

    return PackageDto(**record.model_dump())


@app.patch("/update/partial/{package_id}", response_model=PackageDto)
async def partial_update(package_id: UUID, update_req: UpdatePackageRequest,  session: AsyncSession = Depends(get_session)):
    query = select(Package).where(Package.id==package_id)

    row = (await session.execute(query)).one()

    if not row:
        raise HTTPException(status_code=404, detail="Package not found")
    record = Package(**row._mapping)
    record.sqlmodel_update(update_req.model_dump(exclude_unset=True))

    session.add(record)

    await session.commit()

    await session.refresh()

    return PackageDto(**record.model_dump())

@app.delete("/delete/{package_id}")
async def delete(package_id: UUID,  session: AsyncSession = Depends(get_session)):
    query = select(Package).where(Package.id==package_id)

    row: Package = (await session.execute(query)).one()

    if not row:
        raise HTTPException(status_code=404, detail="Package not found")
    

    session.delete(row)
    await session.commit()

    return {"ok": True}
    

