#!/usr/bin/env python3
import fitz  # PyMuPDF

# Test extracting images from PDF
pdf_path = 'WSDOT Airfields/andersonfield.pdf'

try:
    doc = fitz.open(pdf_path)
    print(f"Pages: {len(doc)}")
    
    # Extract images from first page
    page = doc[0]
    image_list = page.get_images()
    print(f"Images on page: {len(image_list)}")
    
    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        
        # Save the image
        image_filename = f"test_image.{image_ext}"
        with open(image_filename, "wb") as img_file:
            img_file.write(image_bytes)
        print(f"Saved image: {image_filename}")
    
    doc.close()
except Exception as e:
    print(f"Error: {e}")
