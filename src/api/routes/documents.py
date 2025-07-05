from fastapi import UploadFile, File, APIRouter
from pydantic import BaseModel
import shutil
import uuid
import os
import python_multipart



router = APIRouter()



@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        return {"error": "Invalid file type. Please upload a PDF document."}
    
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    
    job_id = str(uuid.uuid4())
    file_extension = ".pdf"
    unique_filename = f"{job_id}{file_extension}"
    
    try:
        with open(f"{upload_dir}/{unique_filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        return {"error": f"Failed to save file: {str(e)}"}
    
    return {"job_id": job_id}
    