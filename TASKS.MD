# LunarTree Software Development Intern - Backend Assignment

## Task Description

Create a robust API service that processes PDF documents, extracts information using a LLM, integrates with a third-party API, and persists data.

## Core Features

1. **PDF Document Upload API Endpoint**
    - Implement `POST /api/documents/upload` endpoint
    - Accept PDF file uploads
    - Return a unique `job_id` upon successful upload

2. **PDF Parsing & LLM Integration**
    - Extract textual content from uploaded PDF using appropriate library (e.g., pdfplumber, PyPDF2)
    - Use a free LLM Model API (Google Gemma, Hugging Face, etc.) to identify GitHub usernames of tech companies mentioned in the document
    - Handle LLM API errors and rate limits gracefully

3. **GitHub Organization Data Retrieval**
    - Use the extracted company username to call the GitHub API (Organizations endpoint)
    - Search for the organization and its public members

4. **Data Persistence with SQLite**
    - Store relevant data in SQLite database:
      - Original PDF filename
      - Extracted company name (if successful)
      - List of GitHub members (if found)
      - Timestamp of completion or failure
    - Design an efficient database schema

5. **Deployment**
    - Deploy application on cloud provider (AWS/DigitalOcean/Google Cloud)
    - Share working link

## Optional Bonus Features

1. **Queue Implementation**
    - Process tasks asynchronously
    - Avoid blocking on upload by offloading operations to a dedicated queue
    - Provide immediate response to user
    - Add 30-300s break to simulate long process for status endpoints

2. **Job Status Inquiry API Endpoint**
    - Implement `GET /api/documents/status/{job_id}` endpoint
    - Allow clients to query processing job status
    - Return extracted company_name and github_members data for completed jobs

## Important Notes

- Do not use AI to generate code for this assignment
- Create a public GitHub repository with atomic commits