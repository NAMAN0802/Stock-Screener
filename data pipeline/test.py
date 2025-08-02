from sqlalchemy import create_engine,Integer,String,Column,UniqueConstraint,Index
from sqlalchemy.orm import declarative_base,sessionmaker

Base = declarative_base()

class Demo(Base):
    __tablename__ = 'demo'
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(50))
    __table_args__ = (UniqueConstraint('name'),
                      Index('name_idx', 'name')
                      )

engine=create_engine("postgresql://naman:password@localhost:5432/stock_screener",echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

demo = Demo(name="naman")
demo2 = Demo(name="kridhav")
session.add(demo)
session.add(demo2)
session.commit()