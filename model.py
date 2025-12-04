from pydantic import BaseModel, field_validator


class Model(BaseModel):
    numbers: list[int] = []
    
    @field_validator("numbers")
    @classmethod
    def ensure_unique(cls, numbers):
        if len(set(numbers)) != len(numbers):
            raise ValueError("elements must be unique")
        return numbers