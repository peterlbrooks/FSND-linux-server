from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Category, User, Base

engine = create_engine('postgresql://catalog:catalogu@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
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


user = User(name = "Admin1217")
session.add(user)
session.commit()


category = Category(name = "Soccer",creatorID=1)
session.add(category)
session.commit()

category = Category(name = "Basketball",creatorID=1)
session.add(category)
session.commit()

category = Category(name = "Baseball",creatorID=1)
session.add(category)
session.commit()

category = Category(name = "Frisbee",creatorID=1)
session.add(category)
session.commit()

category = Category(name = "Snowboarding",creatorID=1)
session.add(category)
session.commit()

category = Category(name = "Rock Climbing",creatorID=1)
session.add(category)
session.commit()

category = Category(name = "Foosball",creatorID=1)
session.add(category)
session.commit()

category = Category(name = "Skiiing",creatorID=1)
session.add(category)
session.commit()

category = Category(name = "Hockey",creatorID=1)
session.add(category)
session.commit()

print "categories created!"
