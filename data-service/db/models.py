from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(Integer, primary_key=True)
    type = Column(String)  # 'state', 'county', 'city', 'zip'
    name = Column(String)
    state_code = Column(String(2))
    zip_code = Column(String(5), nullable=True)
    
    # Relationships
    housing_data = relationship("HousingData", back_populates="location")
    mortgage_data = relationship("MortgageData", back_populates="location")

class HousingData(Base):
    __tablename__ = 'housing_data'
    
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'))
    date = Column(DateTime)
    median_price = Column(Float)
    median_price_sqft = Column(Float)
    median_dom = Column(Integer)  # Days on Market
    inventory = Column(Integer)
    new_listings = Column(Integer)
    price_reduced = Column(Integer)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    location = relationship("Location", back_populates="housing_data")

class MortgageData(Base):
    __tablename__ = 'mortgage_data'
    
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'))
    date = Column(DateTime)
    rate_30yr_fixed = Column(Float)
    rate_15yr_fixed = Column(Float)
    rate_5yr_arm = Column(Float)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    location = relationship("Location", back_populates="mortgage_data") 