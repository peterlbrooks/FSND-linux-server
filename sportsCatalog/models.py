from sqlalchemy import Column,Integer,String, ForeignKey,DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            #Valid Token, but expired
            return None
        except BadSignature:
            #Invalid Token
            return None
        user_id = data['id']
        return user_id

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=True)
    creatorID = Column(Integer, ForeignKey('user.id'))
    #children = relationship("CategoryItem")


# We added this serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'creatorID': self.creatorID
        }


class CategoryItem(Base):
    __tablename__ = 'categoryItem'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    dateUpdated  = Column(DateTime())
    categoryOwnerID = Column(Integer, ForeignKey('category.id'))
    # categoryOwnerName added to avoid having to get name via a call to Category
    categoryOwnerName = Column(String(250))
    creatorID = Column(Integer, ForeignKey('user.id'))

    UniqueConstraint('name', 'categoryOwnerID')

# We added this serialize function to be able to send JSON objects in a
# serializable format
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'dateUpdated': self.dateUpdated,
            'categoryOwnerID': self.categoryOwnerID,
            'categoryOwnerName': self.categoryOwnerName,
            'creatorID': self.creatorID
        }


engine = create_engine('postgresql://catalog:catalogu@localhost/catalog')


Base.metadata.create_all(engine)
