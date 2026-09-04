from pydantic import BaseModel


class HealthRead(BaseModel):
    status: str
    service: str
    version: str


class ReadyRead(BaseModel):
    status: str
    database: str
