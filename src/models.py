from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class White(Base):
	__tablename__ = 'white_cards'
	id = Column(Integer, primary_key = True)
	text = Column(String)
	is_selected = Column(Boolean, default = False)
	def __repr__(self):
		return self.text

class Black(Base):
	__tablename__ = 'black_cards'
	id = Column(Integer, primary_key = True)
	text = Column(String)
	pick = Column(Integer)
	def __repr__(self):
		return f"{self.text}, {self.pick}"





player_scores_m2m = Table(
	'player_scores_m2m',
	Base.metadata,
	Column('room_id', Integer, ForeignKey('rooms.id', ondelete="CASCADE")),
	Column('player_id', Integer, ForeignKey('players.id', ondelete="CASCADE"))
)


player_white_cards = Table(
	'player_white_cards',
	Base.metadata,
	Column('player_id', Integer, ForeignKey('players.id',  ondelete="CASCADE")),
	Column('card_id', Integer, ForeignKey('white_cards.id',  ondelete="CASCADE"))
)


class Player(Base):
	__tablename__ = 'players'
	id = Column(Integer, primary_key = True)
	nickname = Column(String)
	is_admin = Column(Boolean)
	score = Column(Integer)
	white_cards = relationship('White', cascade="all,delete", secondary = player_white_cards)
	def __repr__(self):
		return self.nickname



class Room(Base):
	__tablename__ = 'rooms'
	id = Column(Integer, primary_key = True)
	link = Column(String)
	players = relationship('Player', cascade="all,delete", secondary = player_scores_m2m)
	game_is_started = Column(Boolean)
	current_judge = Column(Integer, ForeignKey('players.id'))

