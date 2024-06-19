from datetime import datetime
from typing import Annotated, Any, Union, Dict

from pydantic import StringConstraints, model_validator, field_validator
from sqlmodel import Field, SQLModel


class BookBase(SQLModel):
    id: Annotated[str, StringConstraints(min_length=6, max_length=6)] = Field(primary_key=True) # type: ignore
    title: str
    author: str


class BookCreate(BookBase):
    pass


class BookUpdate(SQLModel):
    on_loan: bool
    loanee_id: Annotated[str | None, StringConstraints(min_length=6, max_length=6)] | None = Field(default=None)# type: ignore

    @field_validator('loanee_id', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v

    @model_validator(mode='before')
    @classmethod
    def validate_loan_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get('on_loan') and not data.get('loanee_id'):
                raise ValueError('loanee_id should be included when setting on_loan to True')
            elif not data.get('on_loan') and data.get('loanee_id'):
                raise ValueError('loanee_id should not be included when setting on_loan to False')
        return data


class Book(BookBase, table=True, validate_assignment=True):
    on_loan: bool
    loan_date: datetime | None = Field(default=None)
    loanee_id: Annotated[str | None, StringConstraints(min_length=6, max_length=6)] = Field(default=None) # type: ignore

    def update(self, book_update: BookUpdate):
        update_dict = book_update.model_dump()
        if book_update.on_loan:
            update_dict["loan_date"] = datetime.now()
        else:
            update_dict["loan_date"] = None
        self.sqlmodel_update(update_dict)
