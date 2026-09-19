import cv2
import numpy as np
from fastapi import UploadFile
import fitz # PyMuPDF

async def load_image_from_upload(file: UploadFile) -> np.ndarray:
    """
    Loads an image from an UploadFile object, handling PDFs by rendering the first page.
    """
    content = await file.read()

    # Handle PDF
    if file.content_type == "application/pdf":
        doc = fitz.open(stream=content, filetype="pdf")
        page = doc.load_page(0) # First page
        pix = page.get_pixmap()

        # Convert pixmap to numpy array
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        # Convert RGB to BGR (OpenCV format)
        if pix.n == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

        doc.close()
        return img

    # Handle Images
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Could not decode image")

    return img
