"""
Storage Service — Write-through cache with optional GCS backend.

When GCS_BUCKET is set, files are persisted to Google Cloud Storage and
the local filesystem acts as a fast cache.  When GCS_BUCKET is unset
(local dev), everything stays on local disk only — no behaviour change.

Usage:
    from app.services.storage_service import storage

    # Read (checks local cache, then GCS, returns None if missing)
    data = storage.read("experiences/generated_foo.json")

    # Write (writes to local disk + GCS if configured)
    storage.write("generated_images/casino/location_lobby.png", image_bytes)

    # Check existence
    if storage.exists("generated_images/casino/npc_guard.png"):
        ...

    # Get a local path guaranteed to have the file (for FileResponse)
    path = storage.local_path("generated_images/casino/location_lobby.png")
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_BACKEND_ROOT = Path(__file__).parent.parent.parent  # backend/


class StorageService:
    def __init__(self):
        self._bucket_name: Optional[str] = None
        self._gcs_client = None
        self._bucket = None
        self._local_root = _BACKEND_ROOT

    def configure(self, bucket_name: Optional[str] = None):
        """Call once at startup. If bucket_name is provided, enables GCS."""
        self._bucket_name = bucket_name or os.getenv("GCS_BUCKET")
        if self._bucket_name:
            try:
                from google.cloud import storage as gcs
                self._gcs_client = gcs.Client()
                self._bucket = self._gcs_client.bucket(self._bucket_name)
                logger.info(f"Storage: GCS enabled — bucket={self._bucket_name}")
            except Exception as e:
                logger.warning(f"Storage: GCS init failed ({e}), falling back to local only")
                self._bucket_name = None
        else:
            logger.info("Storage: Local-only mode (GCS_BUCKET not set)")

    @property
    def _gcs_enabled(self) -> bool:
        return self._bucket is not None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read(self, key: str) -> Optional[bytes]:
        """Read a file by key (relative to backend/). Returns bytes or None."""
        local = self._local_root / key
        if local.exists():
            return local.read_bytes()

        if self._gcs_enabled:
            return self._gcs_download(key, local)

        return None

    def read_text(self, key: str) -> Optional[str]:
        """Read a text file by key. Returns string or None."""
        data = self.read(key)
        return data.decode("utf-8") if data else None

    def write(self, key: str, data: bytes):
        """Write data to local disk and (if enabled) GCS."""
        local = self._local_root / key
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(data)

        if self._gcs_enabled:
            self._gcs_upload(key, data)

    def write_text(self, key: str, text: str):
        """Write text to local disk and (if enabled) GCS."""
        self.write(key, text.encode("utf-8"))

    def exists(self, key: str) -> bool:
        """Check if a file exists locally or in GCS."""
        if (self._local_root / key).exists():
            return True
        if self._gcs_enabled:
            blob = self._bucket.blob(key)
            return blob.exists()
        return False

    def local_path(self, key: str) -> Optional[Path]:
        """
        Return a local Path to the file, downloading from GCS if needed.
        Returns None if the file doesn't exist anywhere.
        """
        local = self._local_root / key
        if local.exists():
            return local

        if self._gcs_enabled:
            data = self._gcs_download(key, local)
            if data is not None:
                return local

        return None

    def delete_local(self, key: str) -> bool:
        """Delete a file from local disk only. Returns True if deleted."""
        local = self._local_root / key
        if local.exists():
            local.unlink()
            logger.debug(f"Storage: deleted local {key}")
            return True
        return False

    def list_files(self, prefix: str, suffix: str = "") -> list[str]:
        """List file keys under a prefix. Checks local first, then GCS."""
        keys = set()

        local_dir = self._local_root / prefix
        if local_dir.is_dir():
            for f in local_dir.iterdir():
                if f.is_file() and f.name.endswith(suffix):
                    keys.add(f"{prefix}/{f.name}")

        if self._gcs_enabled:
            blobs = self._bucket.list_blobs(prefix=prefix)
            for blob in blobs:
                if blob.name.endswith(suffix):
                    keys.add(blob.name)

        return sorted(keys)

    # ------------------------------------------------------------------
    # GCS internals
    # ------------------------------------------------------------------

    def _gcs_download(self, key: str, local: Path) -> Optional[bytes]:
        try:
            blob = self._bucket.blob(key)
            if not blob.exists():
                return None
            data = blob.download_as_bytes()
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(data)
            logger.debug(f"Storage: downloaded {key} from GCS")
            return data
        except Exception as e:
            logger.warning(f"Storage: GCS download failed for {key}: {e}")
            return None

    def sync_local_to_gcs(self, prefix: str):
        """Upload all local files under prefix to GCS. Call after generation."""
        if not self._gcs_enabled:
            return
        local_dir = self._local_root / prefix
        if not local_dir.is_dir():
            return
        count = 0
        for f in local_dir.rglob("*"):
            if f.is_file():
                key = str(f.relative_to(self._local_root))
                self._gcs_upload(key, f.read_bytes())
                count += 1
        if count:
            logger.info(f"Storage: synced {count} files from {prefix} to GCS")

    def _gcs_upload(self, key: str, data: bytes):
        try:
            blob = self._bucket.blob(key)
            content_type = "image/png" if key.endswith(".png") else "application/octet-stream"
            if key.endswith(".json"):
                content_type = "application/json"
            elif key.endswith(".md"):
                content_type = "text/markdown"
            blob.upload_from_string(data, content_type=content_type)
            logger.debug(f"Storage: uploaded {key} to GCS")
        except Exception as e:
            logger.warning(f"Storage: GCS upload failed for {key}: {e}")


# Singleton instance — import this
storage = StorageService()
