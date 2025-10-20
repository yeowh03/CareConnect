from werkzeug.utils import secure_filename
import os, time, uuid


# ---------- file upload (Supabase) ----------
def upload_image_to_supabase(file_storage, supabase, bucket: str) -> str:
    if not file_storage or file_storage.filename == "":
        raise ValueError("Image is required")
    if not (file_storage.mimetype or "").startswith("image/"):
        raise ValueError("File must be an image")

    original = secure_filename(file_storage.filename)
    ext = os.path.splitext(original)[1].lower()
    unique = f"{uuid.uuid4().hex}{ext}"
    dirpath = time.strftime("%Y/%m/%d")
    storage_path = f"{dirpath}/{unique}"

    data = file_storage.read()
    file_storage.stream.seek(0)

    resp = supabase.storage.from_(bucket).upload(
        file=data, path=storage_path,
        file_options={"content-type": file_storage.mimetype, "upsert": False},
    )
    if getattr(resp, "status_code", 200) >= 400:
        raise RuntimeError(f"Upload failed: {resp}")

    public_url = supabase.storage.from_(bucket).get_public_url(storage_path)
    if not public_url:
        raise RuntimeError("Could not get public URL for uploaded file")
    return public_url