from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship, backref
from flaskr.database_models import Base

class Instruktor(Base):
    __tablename__ = 'instruktor'
    ID_osoba = Column(Integer, ForeignKey('osoba.ID_osoba'), primary_key=True)
    seniorita = Column(String(10), nullable=False)
    datum_narozeni = Column(Date, nullable=False)
    datum_nastupu = Column(Date, nullable=False)
    image_path = Column(String(255))
    popis = Column(String(255))
    osoba = relationship("Osoba", backref=backref("instruktor", uselist=False))