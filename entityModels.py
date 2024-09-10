# 用于定义接收实体类

from pydantic import BaseModel, validator
from typing import Optional, List

from decimal import Decimal


class SysUser(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None
    user_name: str
    create_time: Optional[str] = None
    del_flag: Optional[str] = None


class OrderBook(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    order_type: str
    order_price: Decimal
    order_amount: Decimal
    processed_amount: Optional[Decimal] = None
    status: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    del_flag: Optional[str] = None


class TradeRecord(BaseModel):
    id: Optional[int] = None
    buyer_id: Optional[int] = None
    seller_id: Optional[int] = None
    trade_price: Decimal
    trade_amount: Decimal
    create_time: Optional[str] = None
    del_flag: Optional[str] = None


class Interval(BaseModel):
    interval: Optional[int] = 1


class Order(BaseModel):
    price: Decimal
    amount: Decimal

    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price must be positive')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError('Amount must be positive')
        return v
