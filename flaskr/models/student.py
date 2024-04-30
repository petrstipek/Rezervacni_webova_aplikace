from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship, backref
from flaskr.database_models import Base

class Zak(Base):
    __tablename__ = 'zak'
    ID_zak = Column(Integer, primary_key=True, autoincrement=True)
    ID_rezervace = Column(Integer, ForeignKey('rezervace.ID_rezervace'), nullable=False)
    jmeno = Column(String(20), nullable=False)
    prijmeni = Column(String(30), nullable=False)
    zkusenost = Column(String(20), nullable=False)
    vek = Column(Integer, nullable=False)
    rezervace = relationship("Rezervace", backref='zak')