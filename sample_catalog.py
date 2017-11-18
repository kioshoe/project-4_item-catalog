import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_format import *

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Clear the tables
session.query(User).delete()
session.query(Category).delete()
session.query(Item).delete()

#Dummy Users
user1 = User(name = 'Jane Doe',
	email = 'janedoe@udacity.com',
	picture = 'https://dummyimage.com/200x200.png/ffffff/000000')
session.add(user1)
session.commit()

user2 = User(name = 'John Smith',
	email = 'johnsmith@udacity.com',
	picture = 'https://dummyimage.com/200x200.png/000000/ffffff')
session.add(user2)
session.commit()

#Dummy Categories
category1 = Category(
	name = "Oxides",
	user_id = 1)
session.add(category1)
session.commit()

category2 = Category(
	name = "Sulphides",
	user_id = 2)
session.add(category2)
session.commit()

#Dummy Items
item1 = Item(
	name = "Cassiterite",
	description = "Cassiterite is an important ore of tin and occurs commonly in high-temperature hydrothermal veins around granitic rocks. It is typically brown to black with a white, grey or brownish streak.",
	category = category1,
	user_id = 1)
session.add(item1)
session.commit()

item2 = Item(
	name = "Chromite",
	description = "A primary ore of chromium, chromite is dark brown to black in colour and is also weakly magnetic. It is commonly found in peridotites and other ultrabasic rocks.",
	category = category1,
	user_id = 1)
session.add(item2)
session.commit()

item3 = Item(
	name = "Hematite",
	description = "Hematite is the principal ore of iron and ranges from metallic steel or silvery grey to a dull, red/brown colour depending on its habit. Economically significant deposits of hematite occur in Precambrian rocks.",
	category = category1,
	user_id = 1)
session.add(item3)
session.commit()

item4 = Item(
	name = "Acanthite",
	description = "A silver ore, acanthite tends to be lead-grey to iron-black in colour with a metallic lustre. It generally occurs in low-temperature hydrothermal vein deposits.",
	category = category2,
	user_id = 2)
session.add(item4)
session.commit()

item5 = Item(
	name = "Argentite",
	description = "Argentite is the higher temperature polymorph of acanthite, which is stable above 177 degrees Celsius.",
	category = category2,
	user_id = 2)
session.add(item5)
session.commit()

item6 = Item(
	name = "Arsenopyrite",
	description = "A principal ore of arsenic, arsenopyrite is silvery white with a metallic lustre. It smells of garlic when struck.",
	category = category2,
	user_id = 2)
session.add(item6)
session.commit()

print "Sample catalog of ore-forming minerals has been created."
