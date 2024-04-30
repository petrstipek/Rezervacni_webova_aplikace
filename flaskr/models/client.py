from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship, backref
from flaskr.database_models import Base

class Klient(Base):
    __tablename__ = 'klient'
    ID_osoba = Column(Integer, ForeignKey('osoba.ID_osoba'), primary_key=True)
    osoba = relationship("Osoba", backref=backref("klient", uselist=False))