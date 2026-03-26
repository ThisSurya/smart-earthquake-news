from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from util.database import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    latitude = Column(String(50), nullable=True)
    longitude = Column(String(50), nullable=True)
    content = Column(Text, nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<News(id={self.id}, latitude='{self.latitude}', longitude='{self.longitude}', datetime='{self.datetime}',   created_at='{self.created_at}', updated_at='{self.updated_at}')>"
