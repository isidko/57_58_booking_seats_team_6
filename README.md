# Шаблон для проектов со стилизатором Ruff

## Основное

1. Базовая версия Python - 3.11.
2. В файле `requirements_style.txt` находятся зависимости для стилистики.
3. В каталоге `src` находится весь код приложения:
   - `src/app/` - основной код приложения (API, модели, схемы и т.д.)
   - `src/alembic/` - файлы миграций Alembic
   - `src/Dockerfile` - Dockerfile
4. В файле `requirements.txt` прописываются базовые зависимости.
5. В каталоге `infra` находятся настроечные файлы проекта (docker-compose, nginx и т.д.). Здесь же размещать файлы для docker compose.
6. В каталоге `tests` находятся все тесты (фикстуры, conftest и пр.).

## Стилистика

Для стилизации кода используется пакеты `Ruff` и `Pre-commit`

Проверка стилистики кода осуществляется командой
```shell
ruff check
```

Если одновременно надо пофиксить то, что можно поиксить автоматически, то добавляем параметр `--fix`
```shell
ruff check --fix
```

Что бы стилистика автоматически проверялась и поправлялась при комитах надо добавить hook pre-commit к git

```shell
pre-commit install
```
## Заметки о БД

### Каскадные операции на уровне ORM

Каскадные операции на уровне ORM используются **ТОЛЬКО НА СТОРОНЕ РОДИТЕЛЯ**!

Ссылка на документацию: https://docs.sqlalchemy.org/en/20/orm/cascades.html

Это означает, что мы используем параметр `cascade` в relationship только на родительской таблице, а не на дочерних.

### Пример: Table и Cafe

**Cafe имеет много Table:**

```python
tables: Mapped[list['Table']] = relationship(
    'Table',
    back_populates='cafe',
    lazy='selectin',
    cascade='save-update, merge, delete',
    passive_deletes=True,  # используется, чтобы не дублировать на уровне ORM DB-уровень ondelete='CASCADE'
    order_by='Table.seat_number',
)
```

**Table имеет один Cafe:**

```python
cafe: Mapped['Cafe'] = relationship(
    'Cafe',
    back_populates='tables',
    lazy='joined',
    # cascade здесь не нужен!
)
```

### M2M

Таблица `dish_cafes` - это связь многие-ко-многим между таблицами `Dish` и `Cafe`.
```python
dish_cafes = Table(
    "dish_cafes",
    Base.metadata,
    Column(
        "dish_id",
        ForeignKey("dishes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "cafe_id",
        ForeignKey("cafes.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
```
Пример таблицы связи многие-ко-многим (M2M) между сущностями Dish и Cafe на SQLAlchemy.
- Используется составной первичный ключ из `dish_id` и `cafe_id`
- ondelete="CASCADE" позволяет автоматически удалять связи при удалении блюда или кафе

В этой M2M таблице используется составной первичный ключ из `dish_id` и `cafe_id`.

Документация: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many

Уникальное ограничение не требуется, так как составной ключ сам по себе ограничивает дубликаты. Например, комбинация `(1,2)` и `(1,2)` как первичный ключ будет **ОГРАНИЧЕНА**

---
Как запустить celery?
PYTHONPATH=src python -m celery -A app.tasks.email worker -l info
Как зайти в rabbitmq dashboard?
0.0.0.0:15672
Как запустить Flower?
PYTHONPATH=src python -m celery -A app.tasks.email flower
Как зайти в него
0.0.0.0:5555
