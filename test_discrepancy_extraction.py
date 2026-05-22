import PyPDF2
import re

def extract_coords_from_pdf(pdf_path):
    """Extract coordinates from a PDF file using the same logic as generate_airfield_list.py"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Latitude patterns - same as in generate_airfield_list.py
    lat_match = re.search(r'Latitude.*?(\d+)\D+(\d+)\D+(\d{2,4})\D*′', text, re.IGNORECASE)
    if lat_match:
        degrees = int(lat_match.group(1))
        minutes = int(lat_match.group(2))
        third_val = lat_match.group(3)
        # If third value > 60, it's decimal minutes (e.g., 4414 -> 44.14), not seconds
        if int(third_val) > 60:
            # Handle decimal minutes: 4414 -> 44.14, 4967 -> 49.67
            minutes = float(f"{minutes}.{third_val}")
            lat = degrees + (minutes / 60)
        else:
            seconds = int(third_val)
            lat = degrees + (minutes / 60) + (seconds / 3600)
    else:
        lat = None
    
    # Longitude patterns
    lon_match = re.search(r'Longitude.*?(\d+)\D+(\d+)\D+(\d{2,4})\D*′', text, re.IGNORECASE)
    if lon_match:
        degrees = int(lon_match.group(1))
        minutes = int(lon_match.group(2))
        third_val = lon_match.group(3)
        # If third value > 60, it's decimal minutes (e.g., 2040 -> 20.40), not seconds
        if int(third_val) > 60:
            # Handle decimal minutes: 2040 -> 20.40, 4967 -> 49.67
            minutes = float(f"{minutes}.{third_val}")
            lon = -(degrees + (minutes / 60))
        else:
            seconds = int(third_val)
            lon = -(degrees + (minutes / 60) + (seconds / 3600))
    else:
        lon = None
    
    return lat, lon, text

# Airfields with discrepancies
discrepancies = [
    ("S16", "CopalisState.pdf", 47.124802, -124.184998),
    ("0W7", "FloathavenSPB.pdf", 48.728199, -122.335999),
    ("83Q", "PortofPoulsbo.pdf", 47.734001, -122.647003),
    ("8W3", "Mansfield.pdf", 47.809244, -119.637191),
    ("44T", "HoskinsField.pdf", 46.992438, -122.828003),
    ("1S2", "DarringtonMunicipal.pdf", 48.258598, -121.610001),
    ("W37", "AmericanLake.pdf", 47.141499, -122.560997),
    ("D69", "RogersburgState.pdf", 46.074401, -116.966003),
    ("38W", "LyndenMunicipal.pdf", 48.955898, -122.458000),
    ("W39", "RocheHarbor.pdf", 48.610838, -123.160000),
    ("W33", "FridayHarborSPB.pdf", 48.537300, -123.010002),
    ("13W", "CamanoIsland.pdf", 48.257000, -122.436996),
    ("70S", "MeadFlyingService.pdf", 47.787201, -117.358002),
]

pdf_dir = "Washington Airfield PDFs/"

for code, filename, oa_lat, oa_lon in discrepancies:
    pdf_path = pdf_dir + filename
    print(f"\n{code} - {filename}")
    print(f"OurAirports: {oa_lat:.6f}, {oa_lon:.6f}")
    
    try:
        lat, lon, text = extract_coords_from_pdf(pdf_path)
        if lat and lon:
            print(f"PDF extracted: {lat:.6f}, {lon:.6f}")
            print(f"Difference: {abs(lat - oa_lat):.6f}, {abs(lon - oa_lon):.6f}")
        else:
            print("Could not extract coordinates")
            # Show lines with coordinate patterns
            for line in text.split('\n'):
                if '°' in line and ('N' in line or 'W' in line):
                    print(f"  {line.strip()}")
    except Exception as e:
        print(f"Error: {e}")
