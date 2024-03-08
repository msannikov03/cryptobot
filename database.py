from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    binance_api_key = Column(String, nullable=False)
    binance_api_secret = Column(String, nullable=False)
    trades = relationship("Trade", backref="user")

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id})>"

class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    asset = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price_of_purchase = Column(Float, nullable=False)
    timestamp_of_purchase = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (f"<Trade(asset={self.asset}, quantity={self.quantity}, "
                f"price_of_purchase={self.price_of_purchase}, "
                f"timestamp_of_purchase={self.timestamp_of_purchase})>")

engine = create_engine('sqlite:///trading_bot.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def add_user(telegram_id, binance_api_key, binance_api_secret):
    session = Session()
    new_user = User(telegram_id=telegram_id, binance_api_key=binance_api_key, binance_api_secret=binance_api_secret)
    session.add(new_user)
    session.commit()
    session.close()

def add_trade(user_telegram_id, asset, quantity, price_of_purchase):
    session = Session()
    user = session.query(User).filter_by(telegram_id=user_telegram_id).first()
    if user:
        new_trade = Trade(user_id=user.id, asset=asset, quantity=quantity, price_of_purchase=price_of_purchase)
        session.add(new_trade)
        session.commit()
    session.close()

def get_user_trades(user_telegram_id):
    session = Session()
    user = session.query(User).filter_by(telegram_id=user_telegram_id).first()
    if user:
        trades = session.query(Trade).filter_by(user_id=user.id).all()
        session.close()
        return trades
    session.close()
    return None