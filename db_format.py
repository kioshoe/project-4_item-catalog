import os, sys, datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

def current_time():
	return datetime.datetime.now()

class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

class Category(Base):
	__tablename__ = 'category'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	date = Column(DateTime, default=current_time, onupdate=current_time)
	item = relationship('Item', cascade='all, delete-orphan')
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		"""Returns catalog object data in easily serializeable format"""
		return {
			'name': self.name,
			'id': self.id
		}

class Item(Base):
	__tablename__ = 'item'

	id = Column(Integer, primary_key=True)
	name = Column(String(90), nullable=False)
	description = Column(String(250))
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)
	date = Column(DateTime, default=current_time, onupdate=current_time)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		"""Returns catalog object data in easily serializeable format"""
		return {
			'name': self.name,
			'description': self.description,
			'id': self.id,
			'category': self.category.name
		}

engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
