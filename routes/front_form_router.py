from fastapi import APIRouter,Form,Depends,status,HTTPException,Response
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from db.deps import get_conection
from db.model import Notes
from db.model import User   
from schema.user_schema import User_schema,User_Schema_Output
from schema.notes_schema import Note_Schema
from use_case.user_use_cases import User_use_cases
from use_case.notes_use_cases import Notes_Use_Case
from security.user import create_access_token,get_current_user,decode_token,get_user_from_payload

from passlib.context import CryptContext

front_router = APIRouter(prefix="/front",tags=["Front"])

crypt =CryptContext(schemes=["sha256_crypt"])



templates = Jinja2Templates(directory="templates")


@front_router.get("/")
def read_front(request:Request):
    return templates.TemplateResponse(request=request,name="index.html")

@front_router.post("/result-form",response_model=User_Schema_Output)
def post_front(fname:str=Form(...),cpf:str= Form(...),password:str= Form(...),db_session:Session = Depends(get_conection)):
    person = User_schema(name=fname,cpf=cpf,password=password)
    uc = User_use_cases(db_session=db_session)
    uc.post_user(person)
    return person

@front_router.post("/get-token")
def get_token(response:Response,forms:OAuth2PasswordRequestForm = Depends(),db_session:Session = Depends(get_conection)):
   
    
    user = db_session.query(User).where(User.name==forms.username).first()
    if not user or not crypt.verify(forms.password,user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Usuario ou senha incorreto")
    access_token = create_access_token(data={"sub":forms.username})
    return {"access_token": access_token,"token_type":"bearer"}
    



@front_router.post("/notes")
def post_note(token:str=Form(...),title:str=Form(...),note:str=Form(...),db_session:Session = Depends(get_conection)):
    payload = decode_token(token=token)
    current_user = get_user_from_payload(db_session=db_session,payload=payload)
    notation = Note_Schema(title=title,text=note)
    uc= Notes_Use_Case(db_session=db_session)
    uc.post_not(notation,current_user)
    return RedirectResponse(url=f"/front/notes/{token}", status_code=status.HTTP_303_SEE_OTHER)

@front_router.get("/notes/{token}")
def read_notes(request:Request,token:str,db_session:Session = Depends(get_conection)):
    payload = decode_token(token=token)
    current_user = get_user_from_payload(db_session=db_session,payload=payload)
    notes = db_session.query(Notes).where(Notes.user_id==current_user.id)
    return templates.TemplateResponse("oi.html",{"request":request,"notes":notes,"user":current_user,"token": token})

@front_router.post("/delete-note/{id}")
def deleteNote(id:int,token:str=Form(...),db_session:Session = Depends(get_conection)):
    payload = decode_token(token=token)
    current_user = get_user_from_payload(db_session=db_session,payload=payload)
    uc = Notes_Use_Case(db_session=db_session)
    uc.delete_note(id = id,user=current_user)
    return RedirectResponse(url=f"/front/notes/{token}", status_code=status.HTTP_303_SEE_OTHER)






    


    