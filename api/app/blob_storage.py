from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

try:  # Azure SDK is available in deployed environments, but local dev can run without it.
    from azure.identity import ManagedIdentityCredential
    from azure.storage.blob import BlobServiceClient
except ImportError:  # pragma: no cover - exercised only when Azure packages are absent.
    ManagedIdentityCredential = None
    BlobServiceClient = None


ALLOWED_CONTEXT_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".doc", ".docx", ".md"}
STORAGE_CONNECTION_STRING = os.getenv("AIHUB_STORAGE_CONNECTION_STRING", "")
STORAGE_CONTAINER_NAME = os.getenv("AIHUB_STORAGE_CONTAINER", "documents")
STORAGE_ACCOUNT_NAME = os.getenv("AIHUB_STORAGE_ACCOUNT_NAME", "")
LOCAL_BLOB_ROOT = Path(
    os.getenv("AIHUB_LOCAL_BLOB_ROOT", str(Path(__file__).resolve().parents[2] / "data" / "blob"))
)


@dataclass(slots=True)
class BlobUploadResult:
    filename: str
    content_type: str
    blob_path: str
    blob_url: str


def _build_blob_service_client() -> BlobServiceClient | None:
    if BlobServiceClient is None or ManagedIdentityCredential is None:
        return None
    if STORAGE_ACCOUNT_NAME:
        return BlobServiceClient(
            account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
            credential=ManagedIdentityCredential(),
        )
    if STORAGE_CONNECTION_STRING:
        return BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    return None


def _validate_context_file(upload: UploadFile) -> tuple[str, str]:
    filename = upload.filename or "context-file"
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_CONTEXT_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Tipo de archivo no soportado")
    return filename, upload.content_type or "application/octet-stream"


def _local_blob_path(tenant_id: str, filename: str) -> Path:
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    blob_name = f"{tenant_id}/context/{timestamp}-{uuid4()}-{filename}"
    return LOCAL_BLOB_ROOT / STORAGE_CONTAINER_NAME / blob_name


def upload_context_file(tenant_id: str, upload: UploadFile) -> BlobUploadResult:
    filename, content_type = _validate_context_file(upload)
    blob_service_client = _build_blob_service_client()

    try:
        if blob_service_client is not None:
            try:
                blob_name = f"{tenant_id}/context/{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{uuid4()}-{filename}"
                blob_client = blob_service_client.get_blob_client(
                    container=STORAGE_CONTAINER_NAME,
                    blob=blob_name,
                )
                blob_client.upload_blob(upload.file, overwrite=True, content_type=content_type)
                blob_path = blob_client.blob_name
                blob_url = blob_client.url
                return BlobUploadResult(
                    filename=filename,
                    content_type=content_type,
                    blob_path=blob_path,
                    blob_url=blob_url,
                )
            except Exception:
                # Dev/validation resilience: if Azure Blob auth/config fails, keep operation available locally.
                upload.file.seek(0)

        local_path = _local_blob_path(tenant_id, filename)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with local_path.open("wb") as target:
            upload.file.seek(0)
            target.write(upload.file.read())
        blob_path = str(local_path.relative_to(LOCAL_BLOB_ROOT))
        return BlobUploadResult(
            filename=filename,
            content_type=content_type,
            blob_path=blob_path,
            blob_url=local_path.resolve().as_uri(),
        )
    finally:
        upload.file.close()