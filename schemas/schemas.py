from pydantic import BaseModel, Field, field_validator
from typing import Optional
import datetime


class TransactionsQuery(BaseModel):
    from_wallet: str = Field(None, description="The wallet address from which the transactions are sent.")
    to_wallet: str = Field(None, description="The wallet address to which the transactions are sent.")
    amount: str = Field(None, description="The amount of the transaction.")
    date_start: Optional[str] = Field(None, description="The start date for the transaction query in the format 'dd-mm-yyyy HH:MM:SS'.")
    date_end: Optional[str] = Field(None, description="The end date for the transaction query in the format 'dd-mm-yyyy HH:MM:SS'.")
    limit: Optional[int] = Field(20, description="The maximum number of transactions to return.")
    only_confirmed: Optional[bool] = Field(True, description="Whether to return only confirmed transactions.")

    @field_validator('amount')
    def validate_amount(cls, value):
        try:
            float(value)
        except ValueError:
            raise ValueError("Amount must be a valid number")
        return value

    @field_validator('date_start', 'date_end')
    def validate_date(cls, value, field):
        if value is not None and value != "string":
            try:
                datetime.datetime.strptime(value, "%d-%m-%Y %H:%M:%S")
            except ValueError:
                raise ValueError(f"{field.name} must be in the format 'dd-mm-yyyy HH:MM:SS'")
        return value


class QRcodeQuery(BaseModel):

    wallet: str
