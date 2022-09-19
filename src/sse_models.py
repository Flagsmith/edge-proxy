from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Environment(Base):
    __tablename__ = "environment"
    key = Column(String, primary_key=True)

    def __repr__(self):
        return f"Environment(key={self.key!r})"


class Identity(Base):
    __tablename__ = "identity"
    identifier = Column(String, primary_key=True)
    environment_key = Column(String)

    def __repr__(self):
        return f"Identity(identifier={self.identifier!r})"
