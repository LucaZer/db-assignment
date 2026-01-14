import os
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import motor.motor_asyncio
from bson import ObjectId
from bson.errors import InvalidId

# Load the MongoDB connection string from a .env file
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# FastAPI 
app = FastAPI(title="Event Management API")

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.event_management_db

# Check Endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "API is up"}


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)

# SECURITY HELPERS
def sanitize_string(value: str):
    """
    Prevent NoSQL injection by blocking MongoDB operators.
    """
    if value is None:
        return value
    if "$" in value or "." in value:
        raise HTTPException(
            status_code=400,
            detail="Invalid characters detected in input"
        )
    return value


def validate_object_id(id: str):
    """
    Validate MongoDB ObjectId to prevent injection via path parameters.
    """
    try:
        return ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")

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

#class Media(BaseModel):
#    """
#    Model representing uploaded media (images/videos).
#    """
#    event_id: str
#    filename: str
#    content_type: Optional[str] = None
#    content: bytes
#    uploaded_at: datetime

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

    Args: event (Event): The event data from the client.

    Returns: Contains a success message and the inserted event ID.
    """
    event.title = sanitize_string(event.title)
    event.description = sanitize_string(event.description)
    event.venue_id = sanitize_string(event.venue_id)

    result = await db.events.insert_one(event.dict())
    return {"message": "Event created", "id": str(result.inserted_id)}


@app.get("/events")
async def get_events():
    """
    Retrieve all events from the database.

    Returns: List of event documents with '_id' as string.
    """
    events = await db.events.find().to_list(100)
    return list_obj_to_str(events)

@app.get("/events/{event_id}")
async def get_event(event_id: str):
    """
    Retrieve a single event by its ID.

    Args: event_id (str): MongoDB ObjectId of the event.

    Returns: Event document.

    Raises: HTTPException: If the event is not found.
    """
    event = await db.events.find_one({"_id": validate_object_id(event_id)})
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

    Returns: Success message.

    Raises: HTTPException: If the event does not exist.
    """
    event.title = sanitize_string(event.title)
    event.description = sanitize_string(event.description)
    event.venue_id = sanitize_string(event.venue_id)

    result = await db.events.update_one(
        {"_id": validate_object_id(event_id)},
        {"$set": event.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event updated"}

@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """
    Delete an event from the database.

    Args: event_id (str): Event ID.

    Returns: Success message.

    Raises: HTTPException: If the event does not exist.   
    """
    result = await db.events.delete_one({"_id": validate_object_id(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted"}


# Attendee Endpoints
@app.post("/attendees")
async def create_attendee(attendee: Attendee):
    """
    Create a new attendee.

    Args: attendee (Attendee): Attendee data.

    Returns: Success message and attendee ID.
    """
    attendee.firstName = sanitize_string(attendee.firstName)
    attendee.lastName = sanitize_string(attendee.lastName)
    #attendee.email = sanitize_string(attendee.email)
    #attendee.phone = sanitize_string(attendee.phone)

    result = await db.attendees.insert_one(attendee.dict())
    return {"message": "Attendee created", "id": str(result.inserted_id)}

@app.get("/attendees")
async def get_attendees():
    """
    Retrieve all attendees.

    Returns: List of attendee documents.
    """
    attendees = await db.attendees.find().to_list(100)
    return list_obj_to_str(attendees)

@app.get("/attendees/{attendee_id}")
async def get_attendee(attendee_id: str):
    """
    Retrieve an attendee by ID.

    Args: attendee_id (str): Attendee ID.

    Returns: Attendee document.

    Raises: HTTPException: If attendee not found.
    """
    attendee = await db.attendees.find_one(
        {"_id": validate_object_id(attendee_id)}
    )
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

    Returns: Success message.
    """
    attendee.firstName = sanitize_string(attendee.firstName)
    attendee.lastName = sanitize_string(attendee.lastName)
    attendee.email = sanitize_string(attendee.email)
    attendee.phone = sanitize_string(attendee.phone)

    result = await db.attendees.update_one(
        {"_id": validate_object_id(attendee_id)},
        {"$set": attendee.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return {"message": "Attendee updated"}

@app.delete("/attendees/{attendee_id}")
async def delete_attendee(attendee_id: str):
    """
    Delete an attendee from the database.

    Args: attendee_id (str): Attendee ID.

    Returns: Success message.
    """
    result = await db.attendees.delete_one(
        {"_id": validate_object_id(attendee_id)}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return {"message": "Attendee deleted"}

# Venue Endpoints
@app.post("/venues")
async def create_venue(venue: Venue):
    """
    Create a new venue.

    Args: venue (Venue): Venue data.

    Returns: Success message and venue ID.
    """
    venue.name = sanitize_string(venue.name)
    venue.address = sanitize_string(venue.address)

    result = await db.venues.insert_one(venue.dict())
    return {"message": "Venue created", "id": str(result.inserted_id)}

@app.get("/venues")
async def get_venues():
    """
    Retrieve all venues.

    Returns: List of venue documents.
    """
    venues = await db.venues.find().to_list(100)
    return list_obj_to_str(venues)

@app.get("/venues/{venue_id}")
async def get_venue(venue_id: str):
    """
    Retrieve a venue by ID.

    Args:
        venue_id (str): Venue ID.

    Returns: Venue document.
    """
    venue = await db.venues.find_one(
        {"_id": validate_object_id(venue_id)}
    )
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

    Returns: Success message.
    """
    venue.name = sanitize_string(venue.name)
    venue.address = sanitize_string(venue.address)

    result = await db.venues.update_one(
        {"_id": validate_object_id(venue_id)},
        {"$set": venue.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Venue not found")
    return {"message": "Venue updated"}

@app.delete("/venues/{venue_id}")
async def delete_venue(venue_id: str):
    """
    Delete a venue from the database.

    Args: venue_id (str): Venue ID.

    Returns: Success message.
    """
    result = await db.venues.delete_one(
        {"_id": validate_object_id(venue_id)}
    )
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

    Returns: Success message and booking ID.
    """
    booking.event_id = sanitize_string(booking.event_id)
    booking.attendee_id = sanitize_string(booking.attendee_id)
    booking.ticket_type = sanitize_string(booking.ticket_type)

    result = await db.bookings.insert_one(booking.dict())
    return {"message": "Booking created", "id": str(result.inserted_id)}

@app.get("/bookings")
async def get_bookings():
    """
    Retrieve all bookings.

    Returns: List of booking documents.
    """
    bookings = await db.bookings.find().to_list(100)
    return list_obj_to_str(bookings)

@app.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """
    Retrieve a booking by ID.

    Args: booking_id (str): Booking ID.

    Returns: Booking document.
    """
    booking = await db.bookings.find_one(
        {"_id": validate_object_id(booking_id)}
    )
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

    Returns: Success message.
    """
    booking.event_id = sanitize_string(booking.event_id)
    booking.attendee_id = sanitize_string(booking.attendee_id)
    booking.ticket_type = sanitize_string(booking.ticket_type)

    result = await db.bookings.update_one(
        {"_id": validate_object_id(booking_id)},
        {"$set": booking.dict()}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {"message": "Booking updated"}

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: str):
    """
    Delete a booking.

    Args: booking_id (str): Booking ID.

    Returns: Success message.
    """
    result = await db.bookings.delete_one(
        {"_id": validate_object_id(booking_id)}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking deleted"}

# Media Endpoints
# Helper Functions for Media Operations

async def upload_media(collection, link_field: str, link_id: str, media_type: str, file: UploadFile):
    """
    Helper function to upload media files to the database.

    Args:
        collection: MongoDB collection to store media.
        link_field (str): Field name to link media (event_id or venue_id).
        link_id (str): ID of the event or venue.
        media_type (str): Type of media (event_poster, promo_video, venue_photo).
        file (UploadFile): Uploaded file.

    Returns: Success message and media document ID.
    """
    content = await file.read()
    doc = {
        link_field: link_id,
        "media_type": media_type,
        "filename": file.filename,
        "content_type": file.content_type,
        "content": content,
        "uploaded_at": datetime.utcnow()
    }
    result = await collection.insert_one(doc)
    return {"message": "Uploaded", "id": str(result.inserted_id)}

async def stream_latest_media(collection, link_field: str, link_id: str, media_type: str):
    """
    Helper function to retrieve and stream the latest media file.

    Args:
        collection: MongoDB collection to query.
        link_field (str): Field name to search (event_id or venue_id).
        link_id (str): ID of the event or venue.
        media_type (str): Type of media to retrieve.

    Returns: StreamingResponse with binary file content.

    Raises: HTTPException: If no media found.
    """
    doc = await collection.find_one(
        {link_field: link_id, "media_type": media_type},
        sort=[("uploaded_at", -1)]
    )
    if not doc:
        raise HTTPException(status_code=404, detail="No media found")
 
    return StreamingResponse(
        io.BytesIO(doc["content"]),
        media_type=doc["content_type"],
        headers={"Content-Disposition": f'inline; filename="{doc["filename"]}"'}
    )


# Media Upload Endpoints

@app.post("/upload_event_poster/{event_id}")
async def upload_event_poster(event_id: str, file: UploadFile = File(...)):
    """
    Upload an event poster image.

    Args:
        event_id (str): ID of the event.
        file (UploadFile): Image file to upload.

    Returns: Success message and media document ID.

    Raises: HTTPException: If file is not an image.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Poster must be an image")
    return await upload_media(db.media, "event_id", event_id, "event_poster", file)
 
@app.post("/upload_promo_video/{event_id}")
async def upload_promo_video(event_id: str, file: UploadFile = File(...)):
    """
    Upload a promotional video for an event.

    Args:
        event_id (str): ID of the event.
        file (UploadFile): Video file to upload.

    Returns: Success message and media document ID.

    Raises: HTTPException: If file is not a video.
    """
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Promo must be a video")
    return await upload_media(db.media, "event_id", event_id, "promo_video", file)
 
@app.post("/upload_venue_photo/{venue_id}")
async def upload_venue_photo(venue_id: str, file: UploadFile = File(...)):
    """
    Upload a photo for a venue.

    Args:
        venue_id (str): ID of the venue.
        file (UploadFile): Image file to upload.

    Returns: Success message and media document ID.

    Raises: HTTPException: If file is not an image.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Venue photo must be an image")
    return await upload_media(db.media, "venue_id", venue_id, "venue_photo", file)
 
# Media Retrieval Endpoints

@app.get("/event_poster/{event_id}")
async def get_event_poster(event_id: str):
    """
    Retrieve the latest event poster for an event.

    Args: event_id (str): Event ID.

    Returns: Streaming response with poster image.

    Raises: HTTPException: If no poster found for event.
    """
    return await stream_latest_media(db.media, "event_id", event_id, "event_poster")
 
@app.get("/promo_video/{event_id}")
async def get_promo_video(event_id: str):
    """
    Retrieve the latest promotional video for an event.

    Args: event_id (str): Event ID.

    Returns: Streaming response with video file.

    Raises: HTTPException: If no promo video found for event.
    """
    return await stream_latest_media(db.media, "event_id", event_id, "promo_video")
 
@app.get("/venue_photo/{venue_id}")
async def get_venue_photo(venue_id: str):
    """
    Retrieve the latest photo for a venue.

    Args: venue_id (str): Venue ID.

    Returns: Streaming response with venue photo image.

    Raises: HTTPException: If no photo found for venue.
    """
    return await stream_latest_media(db.media, "venue_id", venue_id, "venue_photo")