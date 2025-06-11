from sqlalchemy import Column, Integer, String, Float
from config.db import Base

class UserSetting(Base):
    __tablename__ = "user_settings"

    user_id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String, nullable=False, default="binance")
    buy_threshold = Column(Float, nullable=True)
    sell_threshold = Column(Float, nullable=True)
    volume_limit = Column(Float, nullable=True)  # Лимит объёма сделки
