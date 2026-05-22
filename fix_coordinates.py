import re

# Coordinates from OurAirports for the 13 airfields with discrepancies >500m
ourairports_corrections = {
    "S16": (47.124802, -124.184998),  # Copalis State
    "0W7": (48.728199, -122.335999),  # Floathaven SPB
    "83Q": (47.734001, -122.647003),  # Port of Poulsbo
    "8W3": (47.809244, -119.637191),  # Mansfield
    "44T": (46.992438, -122.828003),  # Hoskins Field
    "1S2": (48.258598, -121.610001),  # Darrington Municipal
    "W37": (47.141499, -122.560997),  # American Lake SPB
    "D69": (46.074401, -116.966003),  # Rogersburg State
    "38W": (48.955898, -122.458000),  # Lynden Municipal
    "W39": (48.610838, -123.160000),  # Roche Harbor SPB
    "W33": (48.537300, -123.010002),  # Friday Harbor SPB
    "13W": (48.257000, -122.436996),  # Camano Island
    "70S": (47.787201, -117.358002),  # Mead Flying Service
}

# Read map.html
with open('map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update coordinates for each airfield
for code, (new_lat, new_lon) in ourairports_corrections.items():
    # Pattern to match the airfield entry
    pattern = rf'(\{{\s*lat:\s*)[\d.-]+(\s*,\s*lon:\s*)[\d.-]+(\s*,\s*code:\s*"{code}")'
    
    def replace_coords(match):
        return f"{match.group(1)}{new_lat}{match.group(2)}{new_lon}{match.group(3)}"
    
    content = re.sub(pattern, replace_coords, content)
    print(f"Updated {code}: {new_lat}, {new_lon}")

# Write updated map.html
with open('map.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\nCoordinates updated in map.html")
