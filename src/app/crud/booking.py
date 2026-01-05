from typing import Any

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Booking, BookingTableSlot
from app.schemas.booking import BookingCreate, BookingUpdate


class BookingCRUD(CRUDBase[Booking, BookingCreate, BookingUpdate]):
    """CRUD операции для бронирований.

    GET берем из BASE
    Добавляем метод get_bookings, т.к. чистый get_multi в данном контексте не сработает.
    Переопределяем create, так как в базовом всё приводится к dict перед коммитом,
    а в случае с M2M это не сработает.
    Для заполнения M2M нужны уже ГОТОВЫЕ ORM ОБЪЕКТЫ
    Из сообщения приходит обычный dict.
    Преобразуем их в ORM и сохраняем.
    """

    async def create(
            self,
            session: AsyncSession,
            obj_in: BookingCreate,
            **extra_fields: Any,
    ) -> Booking:
        """Переопределяем base create ,т.к. присутствует M2M.

        Т.к. Create включает в себя создание M2M связи,
        необходимо создавать объекты ORM для M2M и потом сохранить Booking.
        """
        # 1) обычные поля (без relationship)
        data = obj_in.model_dump(exclude={"booking_table_slots"})
        data.update(extra_fields)

        booking = Booking(**data)

        # 2) relationship: превращаем входные элементы в ORM-инстансы.
        # relationship с обычными dict не работают!
        booking.booking_table_slots = [
            BookingTableSlot(table_id=ts.table_id, slot_id=ts.slot_id)
            for ts in obj_in.booking_table_slots
        ]

        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        return booking

    async def get_bookings(
            self,
            session: AsyncSession,
            cafe_id: int | None,
            user_id: int | None,
            active_objects_only: bool = True,
    ) -> list[Booking]:
        """Получение списка бронирований.

        1. Создаем where expr
        2. Вызываем get_multi
        """
        and_statements = []
        if user_id is not None:
            and_statements.append(Booking.user_id == user_id)
        if cafe_id is not None:
            and_statements.append(Booking.cafe_id == cafe_id)
        if and_statements:
            return await self.get_multi(
                session=session,
                active_objects_only=active_objects_only,
                where_expr=and_(*and_statements),
            )
        return await self.get_multi(
            session=session, active_objects_only=active_objects_only,
        )

    async def update(
            self,
            session: AsyncSession,
            db_obj: Booking,
            obj_in: BookingUpdate,
    ) -> Booking:
        """Для заполнения M2M нужны уже ГОТОВЫЕ ORM ОБЪЕКТЫ.

        Из сообщения приходит обычный dict.
        Преобразуем их в ORM и сохраняем.
        """
        data = obj_in.model_dump(exclude_unset=True, exclude_none=False)

        booking_table_slots_dict = data.pop("booking_table_slots", None)

        # обычные поля
        for k, v in data.items():
            setattr(db_obj, k, v)

        # связи (если пришли — заменяем целиком)
        if booking_table_slots_dict is not None:
            db_obj.booking_table_slots = [BookingTableSlot(**x) for x in booking_table_slots_dict]

        await session.commit()
        await session.refresh(db_obj)
        return db_obj


booking_crud = BookingCRUD(Booking)
