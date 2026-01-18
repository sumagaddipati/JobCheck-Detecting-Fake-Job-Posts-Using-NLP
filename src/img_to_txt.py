import pytesseract
from PIL import Image

# Path to tesseract.exe (VERY IMPORTANT)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load image
img = Image.open("static\codealpha.png")   # replace with your image path

# Extract text
text = pytesseract.image_to_string(img, lang="eng")

print(text)
