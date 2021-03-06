from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
	__tablename__ =  'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))


class Category(Base):
	__tablename__ = 'category'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable = False)

	@property
	def serialize(self):
		"""Return object data in easily serializable format"""
		return {
			'id'		: self.id,
			'name'		: self.name,
		}


class Item(Base):
	__tablename__ =  'item'

	id = Column(Integer, primary_key=True)
	title = Column(String(250), nullable=False)
	description = Column(String(250), nullable=False)
	cat_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		"""Return object data in easily serializable format"""
		return {
			'id'		 : self.id,
			'title'		 : self.title,
			'description': self.description,
			'cat_id'     : self.cat_id,
			'user_id'    : self.user_id,
		}

# engine =  create_engine('postgresql+psycopg2:///catalog.db')
engine = create_engine('postgresql+psycopg2://catalog:aaa@localhost/catalog')


Base.metadata.create_all(engine)









