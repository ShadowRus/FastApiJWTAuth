from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from auth import Auth
from schemas import AuthModel
from database import *
import socket

def extract_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP



HOST = extract_ip()
PORT = 8084

app = FastAPI()

security = HTTPBearer()
auth_handler = Auth()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()






@app.post('/signup')
def signup(user_details: AuthModel, db: Session = Depends(get_db)):
    user_temp = db.query(Users).filter(Users.username == user_details.username).first()
    if user_temp != None:
        return JSONResponse(status_code=401, content={'status':'Account already exists'})
    try:
        hashed_password = auth_handler.encode_password(user_details.password)
        user = Users(username = user_details.username, password = hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return JSONResponse(status_code=200, content={'status':'Success'})
    except:
        error_msg = 'Failed to signup user'
        return JSONResponse(status_code=400, content={'status':error_msg})


@app.post('/login')
def login(user_details: AuthModel,db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.username == user_details.username).first()
    if (user == None):
        return HTTPException(status_code=401, detail='Invalid username')
    if (not auth_handler.verify_password(user_details.password, user.password)):
        return HTTPException(status_code=401, detail='Invalid password')
    access_token = auth_handler.encode_token(str(user.username))
    refresh_token = auth_handler.encode_refresh_token(str(user.username))
    return {'access_token': access_token, 'refresh_token': refresh_token}


@app.get('/refresh_token')
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    refresh_token = credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token)
    return {'access_token': new_token}


@app.post('/secret')
def secret_data(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if (auth_handler.decode_token(token)):
        return 'Top Secret data only authorized users can access this info'


@app.get('/notsecret')
def not_secret_data():
    return 'Not secret data'


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT, log_level="debug")