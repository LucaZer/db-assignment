import os
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import motor.motor_asyncio

# Load environment variables
load_dotenv()

app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.event_management_db

# Data Models
class Event(BaseModel):
    title: str
    description: str
    date: str
    venue_id: str
    max_attendees: int

class Attendee(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None

class Venue(BaseModel):
    name: str
    address: str
    capacity: int

class Booking(BaseModel):
    event_id: str
    attendee_id: str
    ticket_type: str
    quantity: int
    
class Media(BaseModel):
    fileName: str
    fileType: str
    mediaType: str  
    url: Optional[str] = None 


# Event Endpoints
@app.post("/events")
async def create_event(event: Event):
    result = await db.events.insert_one(event.dict())
    return {"message": "Event created", "id": str(result.inserted_id)}

@app.get("/events")
async def get_events():
    events = await db.events.find().to_list(100)
    for event in events:
        event["_id"] = str(event["_id"])
    return events

# Upload Event Poster
@app.post("/upload_event_poster/{event_id}")
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    content = await file.read()
    poster_doc = {
        "event_id": event_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.event_posters.insert_one(poster_doc)
    return {"message": "Event poster uploaded", "id": str(result.inserted_id)}
