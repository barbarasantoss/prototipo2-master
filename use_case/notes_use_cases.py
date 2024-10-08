from fastapi import HTTPException,status

from sqlalchemy.orm import Session

from db.model import Notes
from db.model import User

from schema.notes_schema import Note_Schema


class Notes_Use_Case:
    def __init__(self,db_session:Session):
        self.db_session = db_session


    def post_not(self,notes:Note_Schema,user:User):
         
        notation = Notes(notes.title,notes.text,user_id=user.id)
        self.db_session.add(notation)
        try:
            self.db_session.commit()
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        
    def delete_note(self,id:int,user:User):

        notation = self.db_session.query(Notes).where(Notes.id == id,Notes.user_id == user.id).first()
        if not notation:
            print("teste")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        self.db_session.delete(notation)
        try:
            self.db_session.commit()
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)


        
        
        
