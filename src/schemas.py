from pydantic import BaseModel
from .models import Player
class WhiteBase(BaseModel):
	text : str
	class Config:
		orm_mode = True
class BlackBase(BaseModel):
	text : str
	pick : int

	class Config:
		orm_mode = True




class PlayerBase(BaseModel):
	nickname : str
	is_admin : bool = False
	score : int = 0
	white_cards: list[WhiteBase] = []
	
class Player(PlayerBase):
	id: int
	class Config:
		orm_mode = True
class PlayerCreate(PlayerBase):
	pass

class RoomBase(BaseModel):
	link : str | None
	players : list[Player] = []
	game_is_started : bool = False
	

class Room(RoomBase):
	id: int
	class Config:
		orm_mode = True

class RoomCreate(RoomBase):
	pass
