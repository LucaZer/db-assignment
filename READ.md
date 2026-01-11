## Requirements
- Python 3.11+

## Setup Instructions
1. Create a virtual environment
   .venv\Scripts\Activate.ps1
2. Install dependencies:
   pip install -r requirements.txt
3. Create a .env file with:
   MONGO_URI=mongodb+srv://dbUser01:MROcnOx3noO2zfSx@cluster0.sf7ttvx.mongodb.net/Db_Project
4. Run the application:
   uvicorn main:app --reload

## API Documentation
Available at:
http://127.0.0.1:8000/docs
