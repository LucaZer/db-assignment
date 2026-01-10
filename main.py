import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import motor.motor_asyncio
from bson import ObjectId

# Load the MongoDB connection string from a .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# FastAPI 
app = FastAPI(title="Event Management API")

# MongoDB connection
# Using Motor (async MongoDB driver)
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.event_management_db
# Collections used: events, attendees, venues, bookings, media


# Data Models
class Event(BaseModel):
    """
    Model representing an event.
    """
    title: str
    description: str
    date: str
    venue_id: str
    max_attendees: int

class Attendee(BaseModel):
    """
    Model representing an attendee.
    """
    firstName: str
    lastName: str
    email: str
    phone: Optional[str] = None

class Venue(BaseModel):
    """
    Model representing a venue.
    """
    name: str
    address: str
    capacity: int

class Booking(BaseModel):
    """
    Model representing a ticket booking.
    """
    event_id: str
    attendee_id: str
    ticket_type: str
    quantity: int

class Media(BaseModel):
    """
    Model representing uploaded media (images/videos).
    """
    fileName: str
    fileType: str
    mediaType: str 
    url: Optional[str] = None

# Helper Functions
def obj_to_str(document):
    """
    Converts MongoDB ObjectId to string for JSON serialization.
    """
    if document:
        document["_id"] = str(document["_id"])
    return document

def list_obj_to_str(documents):
    """
    Converts a list of MongoDB documents' ObjectId fields to strings.
    """
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    return documents

# Event Endpoints
@app.post("/events")
async def create_event(event: Event):
    """
    Create a new event and store it in the 'events' collection.

    Args:
        event (Event): The event data from the client.

    Returns:
        dict: Contains a success message and the inserted event ID.
    """
    result = await db.events.insert_one(event.dict())
    return {"message": "Event created", "id": str(result.inserted_id)}

@app.get("/events")
async def get_events():
    """
    Retrieve all events from the database.

    Returns:
        list: List of event documents with '_id' as string.
    """
    events = await db.events.find().to_list(100)
    return list_obj_to_str(events)

@app.get("/events/{event_id}")
async def get_event(event_id: str):
    """
    Retrieve a single event by its ID.

    Args:
        event_id (str): MongoDB ObjectId of the event.

    Returns:
        dict: Event document.

    Raises:
        HTTPException: If the event is not found.
    """
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return obj_to_str(event)

@app.put("/events/{event_id}")
async def update_event(event_id: str, event: Event):
    """
    Update an existing event.

    Args:
        event_id (str): Event ID.
        event (Event): Updated event data.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If the event does not exist.
    """
    result = await db.events.update_one({"_id": ObjectId(event_id)}, {"$set": event.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event updated"}

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """
    Delete an event from the database.

    Args:
        event_id (str): Event ID.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: If the event does not exist.
    """
    result = await db.events.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted"}

# ------------------------
# Attendee Endpoints
# ------------------------
@app.post("/attendees")
async def create_attendee(attendee: Attendee):
    """
    Create a new attendee.

    Args:
        attendee (Attendee): Attendee data.

    Returns:
        dict: Success message and attendee ID.
    """
    result = await db.attendees.insert_one(attendee.dict())
    return {"message": "Attendee created", "id": str(result.inserted_id)}

@app.get("/attendees")
async def get_attendees():
    """
    Retrieve all attendees.

    Returns:
        list: List of attendee documents.
    """
    attendees = await db.attendees.find().to_list(100)
    return list_obj_to_str(attendees)

@app.get("/attendees/{attendee_id}")
async def get_attendee(attendee_id: str):
    """
    Retrieve an attendee by ID.

    Args:
        attendee_id (str): Attendee ID.

    Returns:
        dict: Attendee document.

    Raises:
        HTTPException: If attendee not found.
    """
    attendee = await db.attendees.find_one({"_id": ObjectId(attendee_id)})
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return obj_to_str(attendee)

@app.put("/attendees/{attendee_id}")
async def update_attendee(attendee_id: str, attendee: Attendee):
    """
    Update attendee information.

    Args:
        attendee_id (str): Attendee ID.
        attendee (Attendee): Updated data.

    Returns:
        dict: Success message.
    """
    result = await db.attendees.update_one({"_id": ObjectId(attendee_id)}, {"$set": attendee.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return {"message": "Attendee updated"}

@app.delete("/attendees/{attendee_id}")
async def delete_attendee(attendee_id: str):
    """
    Delete an attendee from the database.

    Args:
        attendee_id (str): Attendee ID.

    Returns:
        dict: Success message.
    """
    result = await db.attendees.delete_one({"_id": ObjectId(attendee_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return {"message": "Attendee deleted"}

# Venue Endpoints
@app.post("/venues")
async def create_venue(venue: Venue):
    """
    Create a new venue.

    Args:
        venue (Venue): Venue data.

    Returns:
        dict: Success message and venue ID.
    """
    result = await db.venues.insert_one(venue.dict())
    return {"message": "Venue created", "id": str(result.inserted_id)}

@app.get("/venues")
async def get_venues():
    """
    Retrieve all venues.

    Returns:
        list: List of venue documents.
    """
    venues = await db.venues.find().to_list(100)
    return list_obj_to_str(venues)

@app.get("/venues/{venue_id}")
async def get_venue(venue_id: str):
    """
    Retrieve a venue by ID.

    Args:
        venue_id (str): Venue ID.

    Returns:
        dict: Venue document.
    """
    venue = await db.venues.find_one({"_id": ObjectId(venue_id)})
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return obj_to_str(venue)

@app.put("/venues/{venue_id}")
async def update_venue(venue_id: str, venue: Venue):
    """
    Update venue information.

    Args:
        venue_id (str): Venue ID.
        venue (Venue): Updated data.

    Returns:
        dict: Success message.
    """
    result = await db.venues.update_one({"_id": ObjectId(venue_id)}, {"$set": venue.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Venue not found")
    return {"message": "Venue updated"}

@app.delete("/venues/{venue_id}")
async def delete_venue(venue_id: str):
    """
    Delete a venue from the database.

    Args:
        venue_id (str): Venue ID.

    Returns:
        dict: Success message.
    """
    result = await db.venues.delete_one({"_id": ObjectId(venue_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Venue not found")
    return {"message": "Venue deleted"}

# Booking Endpoints
@app.post("/bookings")
async def create_booking(booking: Booking):
    """
    Create a ticket booking.

    Args:
        booking (Booking): Booking data including event and attendee IDs.

    Returns:
        dict: Success message and booking ID.
    """
    result = await db.bookings.insert_one(booking.dict())
    return {"message": "Booking created", "id": str(result.inserted_id)}

@app.get("/bookings")
async def get_bookings():
    """
    Retrieve all bookings.

    Returns:
        list: List of booking documents.
    """
    bookings = await db.bookings.find().to_list(100)
    return list_obj_to_str(bookings)

@app.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """
    Retrieve a booking by ID.

    Args:
        booking_id (str): Booking ID.

    Returns:
        dict: Booking document.
    """
    booking = await db.bookings.find_one({"_id": ObjectId(booking_id)})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return obj_to_str(booking)

@app.put("/bookings/{booking_id}")
async def update_booking(booking_id: str, booking: Booking):
    """
    Update a booking.

    Args:
        booking_id (str): Booking ID.
        booking (Booking): Updated booking data.

    Returns:
        dict: Success message.
    """
    result = await db.bookings.update_one({"_id": ObjectId(booking_id)}, {"$set": booking.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking updated"}

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: str):
    """
    Delete a booking.

    Args:
        booking_id (str): Booking ID.

    Returns:
        dict: Success message.
    """
    result = await db.bookings.delete_one({"_id": ObjectId(booking_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking deleted"}

# Media Upload Endpoints
@app.post("/upload/event_poster/{event_id}")
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    """
    Upload an event poster.

    Files are stored in the 'media' collection as binary data with metadata:
    - fileName: Name of the uploaded file
    - fileType: MIME type of the file
    - mediaType: "poster"
    - event_id: associated event
    - content: raw bytes
    - uploaded_at: timestamp

    Args:
        event_id (str): ID of the event.
        file (UploadFile): Uploaded file.

    Returns:
        dict: Success message and media document ID.
    """
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
    """
    Upload a promotional video for an event.
    Stored in the 'media' collection similar to posters.
    """
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
    """
    Upload a photo for a venue.
    Stored in the 'media' collection with mediaType = "venue_photo".
    """
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

# Media Retrieval Endpoints
@app.get("/media/{media_id}")
async def get_media(media_id: str):
    """
    Retrieve a media file metadata by its ID.
    Returns file metadata including binary content.

    Args:
        media_id (str): Media document ID.

    Returns:
        dict: Media document including raw file content.
    """
    media = await db.media.find_one({"_id": ObjectId(media_id)})
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return obj_to_str(media)

@app.get("/media/event/{event_id}")
async def get_event_media(event_id: str):
    """
    Retrieve all media associated with a specific event.

    Args:
        event_id (str): Event ID.

    Returns:
        list: List of media documents for the event.
    """
    media_items = await db.media.find({"event_id": event_id}).to_list(100)
    return list_obj_to_str(media_items)

@app.get("/media/venue/{venue_id}")
async def get_venue_media(venue_id: str):
    
    #Retrieve all media associated with a specific venue.

    #Args:
       # venue_id (str): Venue ID.

    #Returns:
        #list: List of media documents for the venue.
   
    media_items = await db.media.find({"venue_id": venue_id}).to_list(100)
    return list_obj_to_str(media_items)
