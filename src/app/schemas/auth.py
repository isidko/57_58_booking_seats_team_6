from pydantic import BaseModel


class Token(BaseModel):
    """Схема ответа пользователю."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Данные, извлечённые из токена JWT."""

    username: str | None = None
    scopes: list[str] = []
