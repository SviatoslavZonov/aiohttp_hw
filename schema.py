from pydantic import BaseModel, validator

class CreateAd(BaseModel):
    header: str
    text: str

    @validator('header')
    def validate_header(cls, value):
        if len(value) < 5:
            raise ValueError("Header must be at least 5 characters long")
        return value

    @validator('text')
    def validate_text(cls, value):
        if len(value) < 10:
            raise ValueError("Text must be at least 10 characters long")
        return value

class UpdateAd(BaseModel):
    header: str = None
    text: str = None

    @validator('header')
    def validate_header(cls, value):
        if value and len(value) < 5:
            raise ValueError("Header must be at least 5 characters long")
        return value

    @validator('text')
    def validate_text(cls, value):
        if value and len(value) < 10:
            raise ValueError("Text must be at least 10 characters long")
        return value