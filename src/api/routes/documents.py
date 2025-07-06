from fastapi import UploadFile, File, APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session
import shutil
import uuid
import os
import threading
import datetime
import time
import json
from typing import List, Optional, Dict, Any

from src.models.database import Job, GitHubMember
from src.models.database import get_db
from src.services.pdf_service import PDFService
from src.services.llm_service import github_name_extractor
from src.services.github_service import GitHubService
from src.config.config import UPLOAD_DIR, SIMULATION_DELAY

router = APIRouter()


class MemberResponse(BaseModel):
    login: str
    avatar_url: Optional[str] = None
    html_url: Optional[str] = None
    member_type: Optional[str] = None


class StatusResponse(BaseModel):
    job_id: str
    status: str
    company_name: Optional[str] = None
    github_members: Optional[List[MemberResponse]] = None
    error_message: Optional[str] = None


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != 'application/pdf':
        return {"error": "Invalid file type. Please upload a PDF document."}
    
    job_id = str(uuid.uuid4())
    file_extension = ".pdf"
    unique_filename = f"{job_id}{file_extension}"
    file_path = f"{UPLOAD_DIR}/{unique_filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        new_job = Job(
            job_id=job_id,
            pdf_filename=unique_filename,
            status="pending",
            created_at=datetime.datetime.now()
        )
        db.add(new_job)
        db.commit()
        
        thread = threading.Thread(target=process_pdf, args=(job_id, file_path))
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        return {"error": f"Failed to save file: {str(e)}"}
    
    return {"job_id": job_id}


@router.get("/status/{job_id}", response_model=StatusResponse)
async def check_status(job_id: str = Path(...), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = StatusResponse(
        job_id=str(job.job_id),
        status=str(job.status),
        company_name=str(job.company_name) if job.company_name else None,  # type: ignore
        error_message=str(job.error_message) if job.error_message else None # type: ignore
    )
    
    if str(job.status) == "completed" and job.company_name: # type: ignore
        members = db.query(GitHubMember).filter(GitHubMember.job_id == job_id).all()
        
        if members:
            member_list = []
            for member in members:
                member_list.append(
                    MemberResponse(
                        login=str(member.login),
                        avatar_url=str(member.avatar_url) if member.avatar_url else None, # type: ignore
                        html_url=str(member.html_url) if member.html_url else None,     # type: ignore
                        member_type=str(member.member_type) if member.member_type else None # type: ignore
                    )
                )
            response.github_members = member_list
    
    return response


def process_pdf(job_id: str, pdf_path: str):
    from src.models.database import SessionLocal
    db = SessionLocal()
    
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            return
            
        setattr(job, 'status', 'processing')
        db.commit()
        
        time.sleep(SIMULATION_DELAY)
        
        pdf_service = PDFService()
        pdf_text = pdf_service.extract_text(pdf_path)
        
        if not pdf_text:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                setattr(job, 'status', 'failed')
                setattr(job, 'error_message', 'Failed to extract text from PDF')
                setattr(job, 'completed_at', datetime.datetime.now())
                db.commit()
            return
        
        github_usernames = github_name_extractor(pdf_text)
        
        if not github_usernames:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = "failed"   # type: ignore
                job.error_message = "No GitHub organizations found in the document" # type: ignore
                job.completed_at = datetime.datetime.now() # type: ignore
                db.commit()
            return
        
        org_name = github_usernames[0]
        
        try:
            github_service = GitHubService()
            org_data = github_service.get_organization_data(org_name, max_members=1000)
            if not org_data["success"]:
                job = db.query(Job).filter(Job.job_id == job_id).first()
                if job:
                    job.status = "failed" # type: ignore
                    job.error_message = f"Organization '{org_name}' not found on GitHub" # type: ignore
                    job.completed_at = datetime.datetime.now()  # type: ignore
                    db.commit()
                return
            members = org_data["github_members"]
            num_members = org_data.get("num_members", len(members))
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.company_name = org_name # type: ignore
                job.status = "completed"    # type: ignore
                job.completed_at = datetime.datetime.now()  # type: ignore
                job.num_members = num_members
                for member in members:
                    db_member = GitHubMember(
                        job_id=job_id,
                        login=member.get('login', ''),
                        avatar_url=member.get('avatar_url', ''),
                        html_url=member.get('html_url', ''),
                        member_type=member.get('type', '')
                    )
                    db.add(db_member)
                db.commit()
        except Exception as e:
            job = db.query(Job).filter(Job.job_id == job_id).first()
            if job:
                job.status = "failed"   # type: ignore
                job.error_message = str(e) # type: ignore
                job.completed_at = datetime.datetime.now()   # type: ignore
                db.commit()
            
    except Exception as e:
        job = db.query(Job).filter(Job.job_id == job_id).first() 
        if job:
            job.status = "failed" # type: ignore
            job.error_message = str(e) # type: ignore
            job.completed_at = datetime.datetime.now() # type: ignore
            db.commit()
    
    finally:
        db.close()
