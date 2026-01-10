import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import motor.motor_asyncio
from bson import ObjectId

# ------------------------
# Load environment variables
# ------------------------
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# ------------------------
# FastAPI app
# ------------------------
app = FastAPI(title="Event Management API")

# ------------------------
# MongoDB connection
# ------------------------
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.event_management_db

# ------------------------
# Data Models
# ------------------------
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
    mediaType: str  # poster, video, venue_photo
    url: Optional[str] = None

# ------------------------
# Helper Functions
# ------------------------
def obj_to_str(document):
    if document:
        document["_id"] = str(document["_id"])
    return document

def list_obj_to_str(documents):
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return documents

# ------------------------
# Event Endpoints
# ------------------------
@app.post("/events")
async def create_event(event: Event):
    result = await db.events.insert_one(event.dict())
    return {"message": "Event created", "id": str(result.inserted_id)}

@app.get("/events")
async def get_events():
    events = await db.events.find().to_list(100)
    return list_obj_to_str(events)

@app.get("/events/{event_id}")
async def get_event(event_id: str):
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return obj_to_str(event)

@app.put("/events/{event_id}")
async def update_event(event_id: str, event: Event):
    result = await db.events.update_one({"_id": ObjectId(event_id)}, {"$set": event.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event updated"}

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    result = await db.events.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted"}

# ------------------------
# Attendee Endpoints
# ------------------------
@app.post("/attendees")
async def create_attendee(attendee: Attendee):
    result = await db.attendees.insert_one(attendee.dict())
    return {"message": "Attendee created", "id": str(result.inserted_id)}

@app.get("/attendees")
async def get_attendees():
    attendees = await db.attendees.find().to_list(100)
    return list_obj_to_str(attendees)

@app.get("/attendees/{attendee_id}")
async def get_attendee(attendee_id: str):
    attendee = await db.attendees.find_one({"_id": ObjectId(attendee_id)})
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return obj_to_str(attendee)

@app.put("/attendees/{attendee_id}")
async def update_attendee(attendee_id: str, attendee: Attendee):
    result = await db.attendees.update_one({"_id": ObjectId(attendee_id)}, {"$set": attendee.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return {"message": "Attendee updated"}

@app.delete("/attendees/{attendee_id}")
async def delete_attendee(attendee_id: str):
    result = await db.attendees.delete_one({"_id": ObjectId(attendee_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return {"message": "Attendee deleted"}

# ------------------------
# Venue Endpoints
# ------------------------
@app.post("/venues")
async def create_venue(venue: Venue):
    result = await db.venues.insert_one(venue.dict())
    return {"message": "Venue created", "id": str(result.inserted_id)}

@app.get("/venues")
async def get_venues():
    venues = await db.venues.find().to_list(100)
    return list_obj_to_str(venues)

@app.get("/venues/{venue_id}")
async def get_venue(venue_id: str):
    venue = await db.venues.find_one({"_id": ObjectId(venue_id)})
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return obj_to_str(venue)

@app.put("/venues/{venue_id}")
async def update_venue(venue_id: str, venue: Venue):
    result = await db.venues.update_one({"_id": ObjectId(venue_id)}, {"$set": venue.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Venue not found")
    return {"message": "Venue updated"}

@app.delete("/venues/{venue_id}")
async def delete_venue(venue_id: str):
    result = await db.venues.delete_one({"_id": ObjectId(venue_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Venue not found")
    return {"message": "Venue deleted"}

# ------------------------
# Booking Endpoints
# ------------------------
@app.post("/bookings")
async def create_booking(booking: Booking):
    result = await db.bookings.insert_one(booking.dict())
    return {"message": "Booking created", "id": str(result.inserted_id)}

@app.get("/bookings")
async def get_bookings():
    bookings = await db.bookings.find().to_list(100)
    return list_obj_to_str(bookings)

@app.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return obj_to_str(booking)

@app.put("/bookings/{booking_id}")
async def update_booking(booking_id: str, booking: Booking):
    result = await db.bookings.update_one({"_id": ObjectId(booking_id)}, {"$set": booking.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking updated"}

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: str):
    result = await db.bookings.delete_one({"_id": ObjectId(booking_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking deleted"}

# ------------------------
# Media Upload Endpoints
# ------------------------
@app.post("/upload/event_poster/{event_id}")
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    content = await file.read()
    media_doc = {
        "fileName": file.filename,
        "fileType": file.content_type,
        "mediaType": "poster",
        "event_id": event_id,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.media.insert_one(media_doc)
    return {"message": "Poster uploaded", "id": str(result.inserted_id)}

@app.post("/upload/promo_video/{event_id}")
async def upload_promo_video(event_id: str, file: UploadFile = File(...)):
    content = await file.read()
    media_doc = {
        "fileName": file.filename,
        "fileType": file.content_type,
        "mediaType": "video",
        "event_id": event_id,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.media.insert_one(media_doc)
    return {"message": "Promo video uploaded", "id": str(result.inserted_id)}

@app.post("/upload/venue_photo/{venue_id}")
async def upload_venue_photo(venue_id: str, file: UploadFile = File(...)):
    content = await file.read()
    media_doc = {
        "fileName": file.filename,
        "fileType": file.content_type,
        "mediaType": "venue_photo",
        "venue_id": venue_id,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await db.media.insert_one(media_doc)
    return {"message": "Venue photo uploaded", "id": str(result.inserted_id)}

# ------------------------
# Media Retrieval Endpoints
# ------------------------
@app.get("/media/{media_id}")
async def get_media(media_id: str):
    media = await db.media.find_one({"_id": ObjectId(media_id)})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return obj_to_str(media)

@app.get("/media/event/{event_id}")
async def get_event_media(event_id: str):
    media_items = await db.media.find({"event_id": event_id}).to_list(100)
    return list_obj_to_str(media_items)

@app.get("/media/venue/{venue_id}")
async def get_venue_media(venue_id: str):
    media_items = await db.media.find({"venue_id": venue_id}).to_list(100)
    return list_obj_to_str(media_items)
