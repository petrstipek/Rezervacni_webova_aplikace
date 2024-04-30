from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship, backref
from flaskr.database_models import Base

class SpravceSkoly(Base):
    __tablename__ = 'spravce_skoly'
    ID_osoba = Column(Integer, ForeignKey('osoba.ID_osoba'), primary_key=True)
    osoba = relationship("Osoba", backref=backref("spravce_skoly", uselist=False))