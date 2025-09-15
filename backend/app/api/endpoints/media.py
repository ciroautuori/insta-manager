from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import aiofiles
from PIL import Image
import subprocess

from app.core.database import get_db
from app.core.security import get_current_admin
from app.core.config import settings
from app.models.media import Media, MediaType, MediaStatus
from app.schemas.media import MediaResponse, MediaUpdate

router = APIRouter()

async def validate_and_process_file(file: UploadFile) -> dict:
    """Valida e processa file media"""
    
    # Verifica tipo MIME
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo file non supportato: {file.content_type}"
        )
    
    # Leggi contenuto file
    content = await file.read()
    
    # Verifica dimensione
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File troppo grande. Massimo: {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Genera nome file unico
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Determina tipo media
    media_type = MediaType.IMAGE if file.content_type.startswith('image/') else MediaType.VIDEO
    
    # Crea directory se non exists
    os.makedirs(settings.MEDIA_STORAGE_PATH, exist_ok=True)
    
    file_path = os.path.join(settings.MEDIA_STORAGE_PATH, unique_filename)
    
    # Salva file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Ottieni metadata
    metadata = {"width": None, "height": None, "duration": None}
    
    try:
        if media_type == MediaType.IMAGE:
            with Image.open(file_path) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
        
        elif media_type == MediaType.VIDEO:
            # Usa ffprobe per metadata video
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        metadata["width"] = stream.get('width')
                        metadata["height"] = stream.get('height')
                        metadata["duration"] = int(float(stream.get('duration', 0)))
                        break
    
    except Exception as e:
        # Non bloccare l'upload se fallisce l'estrazione metadata
        pass
    
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "file_path": file_path,
        "file_size": len(content),
        "mime_type": file.content_type,
        "media_type": media_type,
        **metadata
    }

@router.post("/upload", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    alt_text: Optional[str] = Form(None),
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Upload file media"""
    try:
        # Processa e salva file
        file_data = await validate_and_process_file(file)
        
        # Crea record database
        new_media = Media(
            filename=file_data["filename"],
            original_filename=file_data["original_filename"],
            file_path=file_data["file_path"],
            file_size=file_data["file_size"],
            mime_type=file_data["mime_type"],
            media_type=file_data["media_type"],
            width=file_data["width"],
            height=file_data["height"],
            duration=file_data["duration"],
            alt_text=alt_text,
            status=MediaStatus.READY
        )
        
        db.add(new_media)
        db.commit()
        db.refresh(new_media)
        
        return new_media
        
    except Exception as e:
        # Cleanup file se errore database
        if 'file_data' in locals() and os.path.exists(file_data["file_path"]):
            os.unlink(file_data["file_path"])
        
        if isinstance(e, HTTPException):
            raise e
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Errore upload media: {str(e)}"
        )

@router.get("/", response_model=List[MediaResponse])
async def list_media(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
    media_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Lista media files"""
    query = db.query(Media)
    
    if media_type:
        query = query.filter(Media.media_type == media_type)
    
    media_files = query.order_by(Media.created_at.desc()).offset(offset).limit(limit).all()
    return media_files

@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ottieni dettagli media"""
    media = db.query(Media).filter(Media.id == media_id).first()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media non trovato"
        )
    
    return media

@router.put("/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: int,
    media_update: MediaUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Aggiorna metadata media"""
    media = db.query(Media).filter(Media.id == media_id).first()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media non trovato"
        )
    
    # Aggiorna campi
    update_data = media_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(media, field, value)
    
    db.commit()
    db.refresh(media)
    return media

@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Elimina media file"""
    media = db.query(Media).filter(Media.id == media_id).first()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media non trovato"
        )
    
    # Verifica se media è usato in post
    if media.post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non puoi eliminare media associato a un post"
        )
    
    # Elimina file fisico
    try:
        if os.path.exists(media.file_path):
            os.unlink(media.file_path)
        
        # Elimina thumbnail se exists
        if media.thumbnail_path and os.path.exists(media.thumbnail_path):
            os.unlink(media.thumbnail_path)
    
    except Exception as e:
        # Log errore ma continua
        pass
    
    # Elimina record database
    db.delete(media)
    db.commit()
    
    return {"message": "Media eliminato con successo"}
