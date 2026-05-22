import PyPDF2
import re

def extract_coords_from_pdf(pdf_path):
    """Extract coordinates from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    # Try to find latitude and longitude patterns
    lat_pattern = r'Latitude\s*\n?\s*N\s*(\d+)°\s*(\d+)[′\']\s*(\d+)?\.?(\d+)?\s*[′\']?'
    lon_pattern = r'Longitude\s*\n?\s*W\s*(\d+)°\s*(\d+)[′\']\s*(\d+)?\.?(\d+)?\s*[′\']?'
    
    lat_match = re.search(lat_pattern, text)
    lon_match = re.search(lon_pattern, text)
    
    if lat_match and lon_match:
        lat_deg = int(lat_match.group(1))
        lat_min = int(lat_match.group(2))
        lat_sec = lat_match.group(3)
        lat_sec_dec = lat_match.group(4)
        
        lon_deg = int(lon_match.group(1))
        lon_min = int(lon_match.group(2))
        lon_sec = lon_match.group(3)
        lon_sec_dec = lon_match.group(4)
        
        # Convert to decimal degrees
        if lat_sec and lat_sec_dec:
            lat = lat_deg + lat_min/60 + float(f"{lat_sec}.{lat_sec_dec}")/3600
        elif lat_sec:
            lat = lat_deg + lat_min/60 + lat_sec/3600
        else:
            lat = lat_deg + lat_min/60
        
        if lon_sec and lon_sec_dec:
            lon = -(lon_deg + lon_min/60 + float(f"{lon_sec}.{lon_sec_dec}")/3600)
        elif lon_sec:
            lon = -(lon_deg + lon_min/60 + lon_sec/3600)
        else:
            lon = -(lon_deg + lon_min/60)
        
        return lat, lon, text
    
    return None, None, text

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
    print(f"\n{'='*60}")
    print(f"{code} - {filename}")
    print(f"{'='*60}")
    print(f"OurAirports: {oa_lat:.6f}, {oa_lon:.6f}")
    
    try:
        lat, lon, text = extract_coords_from_pdf(pdf_path)
        if lat and lon:
            print(f"PDF extracted: {lat:.6f}, {lon:.6f}")
            
            # Find coordinate lines in text
            for line in text.split('\n'):
                if 'Latitude' in line or 'Longitude' in line or ('N' in line and '°' in line) or ('W' in line and '°' in line):
                    print(f"  {line.strip()}")
        else:
            print("Could not extract coordinates from PDF")
            # Show lines with coordinate-like patterns
            for line in text.split('\n'):
                if '°' in line and ('N' in line or 'W' in line):
                    print(f"  {line.strip()}")
    except Exception as e:
        print(f"Error: {e}")
