import base64
import io
from PIL import Image


def encode_image(uploaded_file) -> dict:
    """
    Encode a Streamlit UploadedFile to a base64 dict
    suitable for Claude's vision API.
    """
    media_type = uploaded_file.type  # e.g. "image/jpeg"

    img = Image.open(uploaded_file)

    # Resize to stay within Claude's recommended limits
    img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)

    fmt = "JPEG" if "jpeg" in media_type or "jpg" in media_type else "PNG"
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    buffer.seek(0)

    encoded = base64.standard_b64encode(buffer.read()).decode("utf-8")
    return {"media_type": media_type, "data": encoded}
