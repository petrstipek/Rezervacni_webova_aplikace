# FileName: available_times.py
# Description: Defines the database model for available times.
# Author: Petr Štípek
# Date: 2024

from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, UniqueConstraint, DateTime
from flaskr.database_models import Base

class DostupneHodiny(Base):
    __tablename__ = 'dostupne_hodiny'
    ID_hodiny = Column(Integer, primary_key=True)
    datum = Column(Date, nullable=False)
    cas_zacatku = Column(Time, nullable=False)
    stav = Column(String(10), nullable=False)
    typ_hodiny = Column(String(30), nullable=False)
    obsazenost = Column(Integer)
    kapacita = Column(Integer)