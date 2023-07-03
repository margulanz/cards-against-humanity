from sqlalchemy.orm import Session
from sqlalchemy import func, select
from . import models, schemas


def get_white(db: Session, card_id: int):
	return db.query(models.White).filter(models.White.id == card_id).first()

def get_black(db: Session, card_id: int):
	return db.query(models.Black).filter(models.Black.id == card_id).first()

def get_random_n_white(db: Session, n: int):
	cards = db.query(models.White).filter(models.White.is_selected == False).order_by(func.random()).limit(n).all()
	return cards

def get_random_black(db: Session):
	card = db.query(models.Black).filter(models.Black.pick == 1).order_by(func.random()).first()
	return card




def get_player(db: Session, id:int):
	player = db.query(models.Player).filter(models.Player.id == id).first()
	return player
def create_player(db: Session, player: schemas.PlayerCreate):
	player = models.Player(nickname = player.nickname,is_admin = player.is_admin,score = player.score)
	db.add(player)
	db.commit()
	db.refresh(player)
	return player
def delete_player(db: Session, nickname: str):
	db.query(models.Player).filter(models.Player.nickname == nickname).delete()
	db.commit()
def get_room(db:Session, id: int):
	return db.query(models.Room).filter(models.Room.id == id).first()
def create_room(db: Session, room: schemas.RoomCreate):
	room = models.Room(link = room.link, players = room.players)
	db.add(room)
	db.commit()
	db.refresh(room)
	return room