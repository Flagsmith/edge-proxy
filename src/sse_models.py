from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import registry

mapper_registry = registry()
Base = mapper_registry.generate_base()


class Environment(Base):
    __tablename__ = "environment"
    key = Column(String, primary_key=True)

    def __repr__(self):
        return f"Environment(key={self.key!r})"
