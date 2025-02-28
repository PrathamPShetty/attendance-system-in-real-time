from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from deepface import DeepFace
import pandas as pd
import shutil
import os
from datetime import datetime

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store uploaded images
UPLOAD_DIR = "uploads"
DB_PATH = "face_db"  # Path to stored face images for recognition
ATTENDANCE_FILE = "attendance.csv"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_PATH, exist_ok=True)

# Create an attendance file if it doesn't exist
if not os.path.exists(ATTENDANCE_FILE):
    df = pd.DataFrame(columns=["Name", "Time"])
    df.to_csv(ATTENDANCE_FILE, index=False)


@app.post("/mark_attendance")
async def mark_attendance(photo: UploadFile = File(...)):
    file_path = f"{UPLOAD_DIR}/{photo.filename}"
    
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    try:
        # Recognize face from the database
        result = DeepFace.find(img_path=file_path, db_path=DB_PATH, distance_metric="euclidean_l2")
        
        if len(result) > 0 and not result[0].empty:
            matched_person = result[0]["identity"][0].split("/")[-1].split(".")[0]  # Extract Name
            
            # Mark attendance
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df = pd.read_csv(ATTENDANCE_FILE)
            
            # Check if the person is already marked for today
            if not df[(df["Name"] == matched_person) & (df["Time"].str.startswith(datetime.now().strftime("%Y-%m-%d")))].empty:
                return {"message": f"{matched_person} already marked present today."}
            
            new_entry = pd.DataFrame({"Name": [matched_person], "Time": [timestamp]})
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv(ATTENDANCE_FILE, index=False)

            return {"message": f"Attendance marked for {matched_person}", "time": timestamp}
        else:
            return {"error": "Face not recognized in the database"}

    except Exception as e:
        return {"error": str(e)}


@app.get("/attendance")
def get_attendance():
    df = pd.read_csv(ATTENDANCE_FILE)
    return df.to_dict(orient="records")


@app.get("/")
def root():
    return {"message": "Welcome to the Face Recognition Attendance System"}
