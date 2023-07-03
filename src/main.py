
import json
from fastapi import Depends, FastAPI,HTTPException, WebSocket,WebSocketDisconnect, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql import asc,desc
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from random import randrange
from . import crud, models, schemas
from .database import SessionLocal, engine

NUM_OF_CARDS_PER_PLAYER = 5
app = FastAPI()

templates = Jinja2Templates(directory="templates")





@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("room.html", {"request": request})


db = SessionLocal()
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.table = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    async def select_judge(self):
        room = db.query(models.Room).filter_by(id = 1).first()
        judge = room.players[randrange(len(room.players))]
        black_card = crud.get_random_black(db = db)
        data = {
            'action':'select_judge',
            'judge':judge.nickname,
            'black_card':black_card.text
        }
        for connection in self.active_connections:
            await connection.send_json(json.dumps(data))
    async def add_to_table(self, values):
        card = db.query(models.White).filter(models.White.text == values['card']).first()
        player = db.query(models.Player).filter(models.Player.id == values['user_id']).first()
        options = {
            'card':values['card'],
            'player':values['user_id']
        }
        self.table.append(options)
        data = {
            'action':'add_to_table',
            'options':self.table
        }
        for connection in self.active_connections:
            await connection.send_json(json.dumps(data))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()



@app.websocket("/ws/")
async def winner_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    while True:
        data = await websocket.receive_json()
        if data['action'] == 'putOnTable':
            await manager.add_to_table(data)
        else:
            await manager.select_judge()



'''
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_white_cards(self,black_card, white_cards, ws):
        cnt = 0
        data = {
            'black-card':None,
            'white-cards':[]
        }
        white_cards = [card.text for card in white_cards]
        for connection in self.active_connections:
            data['black-card'] = black_card.text
            if connection == ws: # Current judge
                await connection.send_json(json.dumps(data))
                continue

            data['white-cards'] = white_cards[cnt:cnt+5]
            await connection.send_json(json.dumps(data))
            data['white-cards'] = []
            cnt+=5
    async def send_selection(self, white_card):
        for connection in self.active_connections:
            await connection.send_text(f"User selected: {white_card}")
    


manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    db = SessionLocal()
    player = models.Player(nickname = client_id,is_admin = False,score = 0)
    db.add(player)
    db.commit()
    db.refresh(player)
    if db.query(models.Player).count() == 1:
        player.is_admin = True
        db.commit()
    try:
        while True:
            data = await websocket.receive_text()
            white_cards = crud.get_random_n_white(db, NUM_OF_CARDS_PER_PLAYER*len(manager.active_connections))
            black_card  = crud.get_random_black(db)
            await manager.send_white_cards(black_card,white_cards, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        crud.delete_player(db = db, nickname = str(client_id))
manager2 = ConnectionManager()
@app.websocket("/ws/")
async def winner_endpoint(websocket: WebSocket):
    await manager2.connect(websocket)
    while True:
        data = await websocket.receive_text()
        await manager2.send_selection(data)
'''
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/whites/{card_id}', response_model = schemas.WhiteBase)
def get_white(card_id: int,db: Session = Depends(get_db)):
    card = crud.get_white(db = db, card_id = card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@app.get('/blacks/{card_id}', response_model = schemas.BlackBase)
def get_black(card_id: int,db: Session = Depends(get_db)):
    card = crud.get_black(db = db, card_id = card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Card not found")
    return card
@app.get('/whites-random/{n}', response_model = list[schemas.WhiteBase])
def get_white_random(n: int,db: Session = Depends(get_db)):
    cards = crud.get_random_n_white(db = db, n = n)
    if cards is None:
        raise HTTPException(status_code=404, detail="Cards not found")
    return cards
@app.get('/black-random/', response_model = schemas.BlackBase)
def get_black_random(db: Session = Depends(get_db)):
    card = crud.get_random_black(db = db)
    if card is None:
        raise HTTPException(status_code=404, detail="Cards not found")
    return card
@app.get('/player/{id}/',response_model = schemas.Player)
def get_player(id:int, db:Session = Depends(get_db)):
    player = crud.get_player(db = db, id = id)
    return player
@app.post('/player/', response_model = schemas.Player)
def create_player(player: schemas.PlayerCreate,db: Session = Depends(get_db)):
    player = crud.create_player(db = db, player = player)
    cards  = crud.get_random_n_white(db = db, n = 5)
    for card in cards:
        player.white_cards.append(card)
        card.is_selected = True
    room = db.query(models.Room).filter_by(id = 1).first()
    room.players.append(player)
    db.commit()
    return player
@app.delete('/player/{nickname}')
def delete_player(nickname:str, db: Session = Depends(get_db)):
    crud.delete_player(nickname = nickname, db = db)
    return {'status':'ok'}


@app.get('/room/{id}', response_model = schemas.Room)
def get_room(id: int, db: Session = Depends(get_db)):
    room = crud.get_room(db = db, id = id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@app.post('/room/', response_model = schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    room = crud.create_room(db = db, room = room)
    return room




#print(db.query(models.player_scores_m2m).filter_by(room_id = 1).order_by(desc(models.player_scores_m2m.c.player_id)).all()) #returns players in room#1 sorted in descending order


#for player in sorted(room.players, key = lambda x : x.score):
#    print(player)



