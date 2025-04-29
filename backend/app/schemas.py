from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class FileUploadResponse(BaseModel):
    id: int
    filename: str

class FileListItem(BaseModel):
    id: int
    filename: str
    upload_time: datetime
    file_metadata: str

class FileListResponse(BaseModel):
    files: List[FileListItem]

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    file_id: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[Any]

class AdminClearAllResponse(BaseModel):
    status: str
    files_deleted: int
    chats_deleted: int
