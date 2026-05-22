import csv
import re
from io import StringIO
import math
import urllib.request

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers."""
    R = 6371  # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def extract_ourairports_data():
    """Download and parse OurAirports CSV data for Washington state."""
    print("Downloading OurAirports data...")
    url = "https://ourairports.com/data/airports.csv"
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    
    # Parse CSV
    csv_file = StringIO(content)
    reader = csv.DictReader(csv_file)
    
    # Filter for Washington state (US-WA)
    wa_airports = {}
    for row in reader:
        if row.get('iso_region') == 'US-WA':
            ident = row.get('ident') or row.get('gps_code') or row.get('iata_code')
            if ident:
                lat = float(row.get('latitude_deg', 0))
                lon = float(row.get('longitude_deg', 0))
                name = row.get('name', '')
                wa_airports[ident.upper()] = {
                    'lat': lat,
                    'lon': lon,
                    'name': name
                }
    
    print(f"Found {len(wa_airports)} airports in OurAirports for Washington")
    return wa_airports

def extract_map_data():
    """Extract airfield coordinates from map.html."""
    print("Extracting coordinates from map.html...")
    with open('map.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract airfield data from the JavaScript array
    pattern = r'\{\s*lat:\s*([\d.-]+),\s*lon:\s*([\d.-]+),\s*code:\s*"([^"]+)",\s*name:\s*"([^"]+)"'
    matches = re.findall(pattern, content)
    
    airfields = {}
    for lat, lon, code, name in matches:
        airfields[code] = {
            'lat': float(lat),
            'lon': float(lon),
            'name': name
        }
    
    print(f"Found {len(airfields)} airfields in map.html")
    return airfields

def compare_coordinates():
    """Compare OurAirports data with map.html data."""
    ourairports = extract_ourairports_data()
    map_data = extract_map_data()
    
    print("\n" + "="*80)
    print("COORDINATE COMPARISON REPORT")
    print("="*80)
    
    discrepancies = []
    not_in_ourairports = []
    not_in_map = []
    
    # Compare coordinates
    for code, map_info in map_data.items():
        if code in ourairports:
            oa_info = ourairports[code]
            distance = haversine_distance(
                map_info['lat'], map_info['lon'],
                oa_info['lat'], oa_info['lon']
            )
            
            if distance > 0.5:  # More than 500m difference
                discrepancies.append({
                    'code': code,
                    'name': map_info['name'],
                    'map_lat': map_info['lat'],
                    'map_lon': map_info['lon'],
                    'oa_lat': oa_info['lat'],
                    'oa_lon': oa_info['lon'],
                    'distance': distance
                })
        else:
            not_in_ourairports.append({
                'code': code,
                'name': map_info['name'],
                'lat': map_info['lat'],
                'lon': map_info['lon']
            })
    
    # Check for airfields in OurAirports but not in our map
    for code, oa_info in ourairports.items():
        if code not in map_data:
            not_in_map.append({
                'code': code,
                'name': oa_info['name'],
                'lat': oa_info['lat'],
                'lon': oa_info['lon']
            })
    
    # Print results
    if discrepancies:
        print(f"\n⚠️  FOUND {len(discrepancies)} DISCREPANCIES (>500m):")
        print("-" * 80)
        for d in sorted(discrepancies, key=lambda x: x['distance'], reverse=True):
            print(f"\n{d['code']} - {d['name']}")
            print(f"  Map:     {d['map_lat']:.6f}, {d['map_lon']:.6f}")
            print(f"  OurAirports: {d['oa_lat']:.6f}, {d['oa_lon']:.6f}")
            print(f"  Distance: {d['distance']:.3f} km")
    else:
        print("\n✅ No significant coordinate discrepancies found (>500m)")
    
    if not_in_ourairports:
        print(f"\n📋 {len(not_in_ourairports)} airfields in map but not in OurAirports:")
        for a in sorted(not_in_ourairports, key=lambda x: x['code']):
            print(f"  {a['code']} - {a['name']} ({a['lat']:.6f}, {a['lon']:.6f})")
    
    if not_in_map:
        print(f"\n📋 {len(not_in_map)} Washington airports in OurAirports but not in map:")
        for a in sorted(not_in_map, key=lambda x: x['code'])[:20]:  # Show first 20
            print(f"  {a['code']} - {a['name']} ({a['lat']:.6f}, {a['lon']:.6f})")
        if len(not_in_map) > 20:
            print(f"  ... and {len(not_in_map) - 20} more")
    
    print("\n" + "="*80)
    
    return discrepancies, not_in_ourairports, not_in_map

if __name__ == "__main__":
    compare_coordinates()
