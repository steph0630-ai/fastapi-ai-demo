from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI 
from sqlalchemy import String, func,DateTime 
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy.ext.asyncio import create_async_engine


#1.创建异步引擎
ASYNC_DATABASE_URL="mysql+aiomysql://root:li20060524@localhost:3306/FastAPI?charset=utf8"

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo =True, #输出sql日志
    pool_size=10, #设置连接池活跃的连接数
    max_overflow=20 #允许的最大额外连接数
)
#2.定义模型类
#基类，创建时间更新时间
class Base(DeclarativeBase):
    create_time : Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),default=func.now,comment="创建时间")
    update_time : Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),default=func.now,onupdate=func.now(),comment="更新时间")

#用户表
class User(Base):
    __tablename__="user"
    id : Mapped[int] = mapped_column(primary_key=True,comment="用户id")
    name:Mapped[str] = mapped_column(String(255),comment="用户名")
    code:Mapped[str] = mapped_column(String(16),comment="密码")

#3.建表，定义函数建表
async def create_tables():
    async with async_engine.begin()as begin:
       await begin.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app):
    await create_tables()
    yield
    await async_engine.dispose()

app = FastAPI(lifespan=lifespan)           