import csv
import re
from io import StringIO
import math
import urllib.request

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Download OurAirports data
url = "https://ourairports.com/data/airports.csv"
response = urllib.request.urlopen(url)
content = response.read().decode('utf-8')
csv_file = StringIO(content)
reader = csv.DictReader(csv_file)

wa_airports = {}
for row in reader:
    if row.get('iso_region') == 'US-WA':
        ident = row.get('ident') or row.get('gps_code') or row.get('iata_code')
        if ident:
            wa_airports[ident.upper()] = {
                'lat': float(row.get('latitude_deg', 0)),
                'lon': float(row.get('longitude_deg', 0)),
                'name': row.get('name', '')
            }

# Extract map coordinates
with open('map.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'\{\s*lat:\s*([\d.-]+),\s*lon:\s*([\d.-]+),\s*code:\s*"([^"]+)",\s*name:\s*"([^"]+)"'
matches = re.findall(pattern, content)

map_airfields = {}
for lat, lon, code, name in matches:
    map_airfields[code] = {
        'lat': float(lat),
        'lon': float(lon),
        'name': name
    }

# Check 4S6 and W28
for code in ['4S6', 'W28']:
    if code in map_airfields:
        map_info = map_airfields[code]
        print(f"\n{code} - {map_info['name']}")
        print(f"Map: {map_info['lat']:.6f}, {map_info['lon']:.6f}")
        
        if code in wa_airports:
            oa_info = wa_airports[code]
            print(f"OurAirports: {oa_info['lat']:.6f}, {oa_info['lon']:.6f}")
            distance = haversine_distance(map_info['lat'], map_info['lon'], oa_info['lat'], oa_info['lon'])
            print(f"Distance: {distance:.3f} km")
        else:
            print("Not found in OurAirports")
    else:
        print(f"\n{code} not found in map")
