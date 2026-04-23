from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import io
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/extract")
async def extract_text(image: UploadFile = File(...)):
    contents = await image.read()
    img = Image.open(io.BytesIO(contents))
    
    # Extract text using pytesseract (requires tesseract executable installed on OS)
    try:
        # Note: on Windows, pytesseract.pytesseract.tesseract_cmd might need to be set
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        text = pytesseract.image_to_string(img, lang='kor+eng')
    except Exception as e:
        print(f"OCR Error: {e}")
        # fallback to mock parsing if tesseract is not available for testing
        text = "Mock Item: 노가다 목장갑\nSTR: 5\nDEX: 3\n"

    # parse mock item data
    item_name = "Unknown"
    stats = {}
    
    # Very basic parsing based on lines
    lines = text.split('\n')
    for line in lines:
        if "STR:" in line or "STR :" in line:
            parts = line.split(":")
            if len(parts) > 1:
                stats["STR"] = int(re.sub(r'[^0-9]', '', parts[1]))
        elif "DEX:" in line or "DEX :" in line:
            parts = line.split(":")
            if len(parts) > 1:
                stats["DEX"] = int(re.sub(r'[^0-9]', '', parts[1]))
        elif "LUK:" in line or "LUK :" in line:
            parts = line.split(":")
            if len(parts) > 1:
                stats["LUK"] = int(re.sub(r'[^0-9]', '', parts[1]))
        elif "목걸이" in line or "Item" in line or "목장갑" in line or "검" in line:
            item_name = line.strip()
            
    # Mock auto-fill output, if text extraction failed we provide placeholders
    if not stats:
        item_name = "노가다 목장갑 (Mock, OCR failed)"
        stats = {"STR": 0, "DEX": 0, "LUK": 0}

    # Security: check max stats
    for k, v in stats.items():
        if v > 100:
             return {"error": f"Invalid stat value {v} for {k}. Might be manipulated!"}
             
    return {
        "item_name": item_name,
        "stats": stats,
        "raw_text": text
    }
