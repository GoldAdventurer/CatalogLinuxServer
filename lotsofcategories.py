from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadat of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Items for Soccer
newCategory = Category(name = "Soccer")
session.add(newCategory)
session.commit()


item1 = Item(title="Running Shoes", description="Great running shoes that \
	helps you run miles", category=newCategory, user=User1)
session.add(item1)
session.commit()

item1 = Item(title="Running Shoes", description="Great running shoes that \
	helps you run miles", category=newCategory, user=User1)
session.add(item1)
session.commit()

item2 = Item(title="Barcelona T-Shirt", description="A T-Shirt for the best\
	team in spain", category=newCategory, user=User1)
session.add(item2)
session.commit()

item3 = Item(title="Arsenal Jersey", description="You really need this one.",\
	category=newCategory, user=User1)
session.add(item3)
session.commit()

item4 = Item(title="Soccer Ball", description="Robust, sturdy, a ball used for\
	professionals for professionals.", category=newCategory, user=User1)
session.add(item4)
session.commit()

item5 = Item(title="Field Player Gloves", description="The right gloves to\
	protect your hands", category=newCategory, user=User1)
session.add(item5)
session.commit()


# Items for Soccer
newCategory = Category(name = "Basketball")
session.add(newCategory)
session.commit()


item1 = Item(title="Bat", description="The bat", category=newCategory, \
	user=User1)
session.add(item1)
session.commit()

item1 = Item(title="Basketball Shoes", description="Basketball shoes",\
 category=newCategory, user=User1)
session.add(item1)
session.commit()

item2 = Item(title="Leg Sleeves", description="The leg sleeves", \
	category=newCategory, user=User1)
session.add(item2)
session.commit()

item3 = Item(title="Hoops", description="The hoops", category=newCategory,\
	 user=User1)
session.add(item3)
session.commit()

item4 = Item(title="Shorts", description="The shorts", category=newCategory, \
	user=User1)
session.add(item4)
session.commit()

item5 = Item(title="Socks", description="The socks", category=newCategory, \
	user=User1)
session.add(item5)
session.commit()


# Items for Karate
newCategory = Category(name = "Karate")
session.add(newCategory)
session.commit()


item1 = Item(title="Karate Suit", description="The karate suit", \
	category=newCategory, user=User1)
session.add(item1)
session.commit()

item1 = Item(title="Trousers", description="The trousers", \
	category=newCategory, user=User1)
session.add(item1)
session.commit()

item2 = Item(title="Belts", description="The belts", category=newCategory, \
	user=User1)
session.add(item2)
session.commit()

item3 = Item(title="Bags", description="The bags", category=newCategory, \
	user=User1)
session.add(item3)
session.commit()

item4 = Item(title="Floor Mats", description="The floor mats",\
 category=newCategory, user=User1)
session.add(item4)
session.commit()

item5 = Item(title="Body Armour", description="The body armour", \
	category=newCategory, user=User1)
session.add(item5)
session.commit()


# Other categories
newCategory = Category(name = "Baseball")
session.add(newCategory)
session.commit()

newCategory = Category(name = "Frisbee")
session.add(newCategory)
session.commit()

newCategory = Category(name = "Snowboarding")
session.add(newCategory)
session.commit()

newCategory = Category(name = "Rock Climbing")
session.add(newCategory)
session.commit()

newCategory = Category(name = "Football")
session.add(newCategory)
session.commit()

newCategory = Category(name = "Skating")
session.add(newCategory)
session.commit()

newCategory = Category(name = "Hockey")
session.add(newCategory)
session.commit()
# Confirmation
print "added menu items!"

