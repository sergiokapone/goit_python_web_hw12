from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Date, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import MetaData

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    additional_data = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Add foreign key column

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=True)  
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    contacts = relationship('Contact', backref='user')  # Define the relationship backref