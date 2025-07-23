from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    week_day = Column(String)
    hour = Column(String)
    ticket_number = Column(String)
    waiter = Column(Integer)
    product_name = Column(String)
    quantity = Column(Float)
    unitary_price = Column(Float)
    total = Column(Float)
