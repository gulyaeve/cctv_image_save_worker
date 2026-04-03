from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from app.database import async_session_maker
from logging import log


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        try:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            async with async_session_maker() as session:
                result = await session.execute(query)
                return result.mappings().one_or_none()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Data not found"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Data not found"

            log.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None

    @classmethod
    async def find_all(cls, **filter_by):
        try:
            query = select(cls.model.__table__.columns).filter_by(**filter_by).order_by(cls.model.id)
            async with async_session_maker() as session:
                result = await session.execute(query)
                return result.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Data not found"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Data not found"

            log.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None
    
    @classmethod
    async def add(cls, **data):
        try:
            query = insert(cls.model).values(**data).returning(cls.model)
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"

            log.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None

    @classmethod
    async def delete(cls, **filter_by):
        try:
            query = delete(cls.model).filter_by(**filter_by)
            async with async_session_maker() as session:
                await session.execute(query)
                await session.commit()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot delete data"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot delete data"

            log.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None

    # @classmethod
    # async def del_by_ids(cls, ids: list[int]):
    #     for id in ids:
    #         async with async_session_maker() as session:
    #             query = delete(cls.model).filter_by(id=id)
    #             await session.execute(query)
    #             await session.commit()

    
    @classmethod
    async def add_bulk(cls, *data):
        try:
            query = insert(cls.model).values(*data).returning(cls.model.__table__)
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.mappings().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot bulk insert data into table"

            log.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None
        
    @classmethod
    async def update(cls, id: int, **data):
        try:
            query = (
                update(cls.model)
                .where(cls.model.id == id)
                .values(**data)
                .returning(cls.model)
                )
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                return result.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot update data in table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot update data in table"

            log.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None
