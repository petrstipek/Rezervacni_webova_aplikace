# FileName: student.py
# Description: Defines the database model for students.
# Author: Petr Štípek
# Date: 2024

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
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