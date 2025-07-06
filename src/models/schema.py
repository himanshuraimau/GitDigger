from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.models.database import Base


class Job(Base):
    """Job model to track document processing"""
    __tablename__ = 'jobs'
    
    job_id = Column(String, primary_key=True)
    pdf_filename = Column(String, nullable=False)
    status = Column(String, nullable=False, default='pending')  # pending, processing, completed, failed
    company_name = Column(String)
    created_at = Column(DateTime, default=func.current_timestamp())
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    members = relationship("GitHubMember", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Job(job_id='{self.job_id}', status='{self.status}', company_name='{self.company_name}')>"


class GitHubMember(Base):
    """GitHub member model to store organization members"""
    __tablename__ = 'github_members'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey('jobs.job_id', ondelete='CASCADE'), nullable=False)
    login = Column(String, nullable=False)
    avatar_url = Column(String)
    html_url = Column(String)
    member_type = Column(String)
    
    job = relationship("Job", back_populates="members")
    
    def __repr__(self):
        return f"<GitHubMember(id={self.id}, login='{self.login}', job_id='{self.job_id}')>"
