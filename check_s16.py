import PyPDF2
import re

pdf_path = "Washington Airfield PDFs/CopalisState.pdf"
with open(pdf_path, 'rb') as file:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

print("Full text from CopalisState.pdf:")
print("="*60)
print(text)
print("="*60)

# Show lines with coordinate patterns
print("\nLines with coordinate patterns:")
for line in text.split('\n'):
    if '°' in line or 'Latitude' in line or 'Longitude' in line:
        print(f"  {line.strip()}")
