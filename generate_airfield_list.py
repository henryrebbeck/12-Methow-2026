#!/usr/bin/env python3
"""
Generate an HTML file with links to all PDFs in the current directory.
Run this script in the folder containing your PDFs and index.html.
"""

import os
import re
import PyPDF2
import fitz  # PyMuPDF for image extraction
import base64
from pathlib import Path

def extract_airfield_info(filename, pdf_path):
    """Extract FAA code and name from PDF content."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        # Extract FAA code from pattern like "City / Airfield Name  / CODE"
        # Include slashed zero (Ø) in pattern
        code_match = re.search(r'/\s*([A-Z0-9Ø]{3,4})\s*$', text, re.MULTILINE)
        if not code_match:
            code_match = re.search(r'/\s*([A-Z0-9Ø]{3,4})\s', text)
        
        code = code_match.group(1).upper() if code_match else 'UNK'
        # Replace slashed zero (Ø) with regular zero (0)
        code = code.replace('Ø', '0')
        
        # Extract airfield name from pattern like "City / Airfield Name  / CODE"
        name_match = re.search(r'/\s*([^/]+)\s*/', text)
        name = name_match.group(1).strip() if name_match else filename.replace('.pdf', '')
        
        return {
            'code': code,
            'name': name,
            'original_name': filename
        }
    except Exception as e:
        print(f"Error extracting info from {pdf_path}: {e}")
        return {
            'code': 'UNK',
            'name': filename.replace('.pdf', ''),
            'original_name': filename
        }

def extract_airfield_image_base64(pdf_path):
    """Extract the main image from PDF and return as Base64 string."""
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        image_list = page.get_images()
        
        if image_list:
            xref = image_list[0][0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Convert to Base64
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            data_uri = f"data:image/{image_ext};base64,{base64_string}"
            
            doc.close()
            return data_uri
        else:
            doc.close()
            return None
    except Exception as e:
        print(f"Error extracting image from {pdf_path}: {e}")
        return None

def extract_airfield_data(pdf_path):
    """Extract key airfield data from PDF text."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        # Extract CTAF frequency - match pattern like 123.0 or 122.9
        ctaf_match = re.search(r'CTAF[^0-9]*(\d{3})[^\d]*(\d)', text, re.IGNORECASE)
        if ctaf_match:
            ctaf = ctaf_match.group(1) + '.' + ctaf_match.group(2)
        else:
            ctaf = 'N/A'
        
        # Extract AWOS/ASOS frequency
        awos_match = re.search(r'AWOS.*?(\d{3})[^\d]*(\d{3})', text, re.IGNORECASE)
        if awos_match:
            awos = awos_match.group(1) + '.' + awos_match.group(2)
        else:
            awos = 'N/A'
        
        # Extract Elevation - more permissive pattern
        elev_match = re.search(r'ELEV[^0-9]*(\d+)', text, re.IGNORECASE)
        elevation = elev_match.group(1) if elev_match else 'N/A'
        
        # Extract TPA (Traffic Pattern Altitude)
        tpa_match = re.search(r'TPA[^0-9]*(\d+)', text, re.IGNORECASE)
        tpa = tpa_match.group(1) if tpa_match else 'N/A'
        
        # Extract Runway dimensions and direction - handle spacing variations
        runway_match = re.search(r'(\d{1,2}/\d{1,2}).*?(\d{3,5}).*?×.*?(\d{2,3})', text, re.IGNORECASE)
        if runway_match:
            runway_dir = runway_match.group(1)
            length = runway_match.group(2)
            width = runway_match.group(3)
        else:
            # Fallback: try to extract just dimensions
            runway_match = re.search(r'Runway.*?(\d{3,5}).*?×.*?(\d{2,3})', text, re.IGNORECASE)
            if runway_match:
                runway_dir = 'N/A'
                length = runway_match.group(1)
                width = runway_match.group(2)
            else:
                runway_dir = 'N/A'
                length = 'N/A'
                width = 'N/A'
        
        # Extract Latitude - format: N 48° 06′29′ (degrees, minutes, seconds)
        # Handle various prime/special characters between values
        # Also handle compact format like 48° 36′49′ (no space between minutes and seconds)
        # Also handle decimal format like N 47° 31.80′
        # Also handle dash format like 47-08-40.789 (degrees-minutes-seconds.decimal)
        # Also handle format with special chars like N 48° 44�14 ′
        # Some PDFs don't extract N/W, so look for Latitude label
        lat_match = re.search(r'Latitude.*?(\d+)-(\d+)-(\d+)\D+(\d+)', text, re.IGNORECASE)
        if lat_match:
            # Dash format: 47-08-40.789
            degrees = int(lat_match.group(1))
            minutes = int(lat_match.group(2))
            seconds = float(f"{lat_match.group(3)}.{lat_match.group(4)}")
            latitude = degrees + (minutes / 60) + (seconds / 3600)
        else:
            lat_match = re.search(r'Latitude.*?(\d+)\D+(\d+)\.(\d+)', text, re.IGNORECASE)
            if lat_match:
                # Decimal format: 47° 31.80′
                degrees = int(lat_match.group(1))
                minutes = float(f"{lat_match.group(2)}.{lat_match.group(3)}")
                latitude = degrees + (minutes / 60)
            else:
                # Try to match format with special characters between minute parts: N 48° 44�14 ′
                lat_match = re.search(r'Latitude.*?(\d+)\D+(\d+)\D+(\d{2,4})\D*′', text, re.IGNORECASE)
                if lat_match:
                    degrees = int(lat_match.group(1))
                    minutes = int(lat_match.group(2))
                    third_val = lat_match.group(3)
                    # If third value > 60, it's decimal minutes (e.g., 4414 -> 44.14), not seconds
                    if int(third_val) > 60:
                        # Handle decimal minutes: 4414 -> 44.14, 4967 -> 49.67
                        minutes = float(f"{minutes}.{third_val}")
                        latitude = degrees + (minutes / 60)
                    else:
                        seconds = int(third_val)
                        latitude = degrees + (minutes / 60) + (seconds / 3600)
                else:
                    lat_match = re.search(r'Latitude.*?(\d+)\D+(\d+)\D+(\d+)', text, re.IGNORECASE)
                    if lat_match:
                        degrees = int(lat_match.group(1))
                        minutes = int(lat_match.group(2))
                        third_val = int(lat_match.group(3))
                        # If third value > 60, it's decimal minutes (e.g., 30.989), not seconds
                        if third_val > 60:
                            minutes = float(f"{minutes}.{third_val}")
                            latitude = degrees + (minutes / 60)
                        else:
                            seconds = third_val
                            latitude = degrees + (minutes / 60) + (seconds / 3600)
                    else:
                        # Try alternative format
                        lat_match = re.search(r'Lat.*?(\d+)\s*[°\*]\s*(\d+)', text, re.IGNORECASE)
                        if lat_match:
                            degrees = int(lat_match.group(1))
                            minutes = float(lat_match.group(2)) / 100
                            latitude = degrees + (minutes / 60)
                        else:
                            latitude = None
        
        # Extract Longitude - format: W 119° 43′24′ (degrees, minutes, seconds)
        # Handle various prime/special characters between values
        # Also handle compact format like 123° 09′58′ (no space between minutes and seconds)
        # Also handle decimal format like W 122° 18.12′
        # Also handle dash format like 124-11-20.662 (degrees-minutes-seconds.decimal)
        # Also handle format with special chars like W 122° 20�40 ′
        # Some PDFs don't extract N/W, so look for Longitude label
        lon_match = re.search(r'Longitude.*?(\d+)-(\d+)-(\d+)\D+(\d+)', text, re.IGNORECASE)
        if lon_match:
            # Dash format: 124-11-20.662
            degrees = int(lon_match.group(1))
            minutes = int(lon_match.group(2))
            seconds = float(f"{lon_match.group(3)}.{lon_match.group(4)}")
            longitude = -(degrees + (minutes / 60) + (seconds / 3600))
        else:
            lon_match = re.search(r'Longitude.*?(\d+)\D+(\d+)\.(\d+)', text, re.IGNORECASE)
            if lon_match:
                # Decimal format: 122° 18.12′
                degrees = int(lon_match.group(1))
                minutes = float(f"{lon_match.group(2)}.{lon_match.group(3)}")
                longitude = -(degrees + (minutes / 60))
            else:
                # Try to match format with special characters between minute parts: W 122° 20�40 ′
                lon_match = re.search(r'Longitude.*?(\d+)\D+(\d+)\D+(\d{2,4})\D*′', text, re.IGNORECASE)
                if lon_match:
                    degrees = int(lon_match.group(1))
                    minutes = int(lon_match.group(2))
                    third_val = lon_match.group(3)
                    # If third value > 60, it's decimal minutes (e.g., 2040 -> 20.40), not seconds
                    if int(third_val) > 60:
                        # Handle decimal minutes: 2040 -> 20.40, 4967 -> 49.67
                        minutes = float(f"{minutes}.{third_val}")
                        longitude = -(degrees + (minutes / 60))
                    else:
                        seconds = int(third_val)
                        longitude = -(degrees + (minutes / 60) + (seconds / 3600))
                else:
                    lon_match = re.search(r'Longitude.*?(\d+)\D+(\d+)\D+(\d+)', text, re.IGNORECASE)
                    if lon_match:
                        degrees = int(lon_match.group(1))
                        minutes = int(lon_match.group(2))
                        third_val = int(lon_match.group(3))
                        # If third value > 60, it's decimal minutes (e.g., 54.911), not seconds
                        if third_val > 60:
                            minutes = float(f"{minutes}.{third_val}")
                            longitude = -(degrees + (minutes / 60))
                        else:
                            seconds = third_val
                            longitude = -(degrees + (minutes / 60) + (seconds / 3600))
                    else:
                        # Try alternative format
                        lon_match = re.search(r'Lon.*?(\d+)\s*[°\*]\s*(\d+)', text, re.IGNORECASE)
                        if lon_match:
                            degrees = int(lon_match.group(1))
                            minutes = float(lon_match.group(2)) / 100
                            longitude = -(degrees + (minutes / 60))
                        else:
                            longitude = None
        
        return {
            'ctaf': ctaf,
            'awos': awos,
            'elevation': elevation,
            'tpa': tpa,
            'length': length,
            'width': width,
            'runway_dir': runway_dir,
            'latitude': latitude,
            'longitude': longitude
        }
    except Exception as e:
        print(f"Error extracting data from {pdf_path}: {e}")
        return {
            'ctaf': 'N/A',
            'awos': 'N/A',
            'elevation': 'N/A',
            'tpa': 'N/A',
            'length': 'N/A',
            'width': 'N/A',
            'runway_dir': 'N/A'
        }

def generate_html():
    # Get all PDF files in Washington Airfield PDFs subfolder
    pdf_folder = 'Washington Airfield PDFs'
    if not os.path.exists(pdf_folder):
        print(f"Folder '{pdf_folder}' not found!")
        return
    
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in current directory!")
        return
    
    # Sort by code
    airfields = []
    for pdf in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf)
        info = extract_airfield_info(pdf, pdf_path)
        data = extract_airfield_data(pdf_path)
        
        # Extract image as Base64 string
        image_base64 = extract_airfield_image_base64(pdf_path)
        info['image_base64'] = image_base64
        
        info.update(data)
        airfields.append(info)
    
    airfields.sort(key=lambda x: x['name'])
    
    # Generate HTML with HUD overlay layout and PWA support
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <meta name="theme-color" content="#000000">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="manifest.json">
    <title>Airfield Directory</title>
    <script>
        if ('serviceWorker' in navigator) {{
            navigator.serviceWorker.register('sw.js').then(function(registration) {{
                console.log('Service Worker registered with scope:', registration.scope);
            }}).catch(function(error) {{
                console.log('Service Worker registration failed:', error);
            }});
        }}

        // Force reflow on viewport changes for Chrome DevTools
        window.addEventListener('resize', function() {{
            document.body.style.zoom = '1';
        }});
    </script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            width: 100%;
            height: 100%;
            overflow-x: hidden;
        }}

        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f5f5f5;
            --text-primary: #000000;
            --text-secondary: #333333;
            --border-color: #000000;
            --accent-color: #0066cc;
            --hud-bg: rgba(0, 0, 0, 0.85);
            --hud-text: #ffffff;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }}

        .container {{
            padding: 16px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            margin-bottom: 20px;
        }}

        .title {{
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #000;
        }}

        .subtitle {{
            font-size: 18px;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}

        .search-container {{
            margin-bottom: 20px;
            position: sticky;
            top: 16px;
            z-index: 100;
        }}

        .search-input {{
            width: 100%;
            padding: 16px 20px;
            font-size: 18px;
            border: 3px solid var(--border-color);
            border-radius: 12px;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            outline: none;
            font-weight: 500;
        }}

        .search-input:focus {{
            border-color: var(--accent-color);
        }}

        .sort-controls {{
            margin-bottom: 20px;
            display: flex;
            gap: 12px;
        }}

        .sort-btn {{
            flex: 1;
            padding: 16px 24px;
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            border: 3px solid var(--border-color);
            border-radius: 12px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .sort-btn.active {{
            background-color: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
        }}

        .sort-btn:hover {{
            transform: translateY(-2px);
        }}

        .airfield-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .airfield-card {{
            background-color: var(--bg-secondary);
            border: 3px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }}

        .airfield-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }}

        .airfield-card.hidden {{
            display: none;
        }}

        .airfield-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-right: 90px;
        }}

        .airfield-code {{
            font-size: 28px;
            font-weight: 900;
            color: var(--accent-color);
            font-family: monospace;
        }}

        .airfield-name {{
            font-size: 24px;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .airfield-details {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            font-size: 16px;
            color: var(--text-secondary);
        }}

        .detail-item {{
            font-weight: 500;
        }}

        .detail-item span {{
            font-weight: 700;
            color: var(--text-primary);
        }}

        .distance-badge {{
            position: absolute;
            top: 20px;
            right: 20px;
            background-color: var(--accent-color);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
        }}

        /* HUD Overlay */
        .hud-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: var(--hud-bg);
            z-index: 1000;
            display: none;
            flex-direction: column;
            overflow-y: auto;
        }}

        .hud-overlay.active {{
            display: flex;
        }}

        .hud-background {{
            flex: 1;
            background-size: contain;
            background-position: center;
            background-repeat: no-repeat;
            min-height: 50vh;
            position: relative;
            touch-action: pan-x pan-y pinch-zoom;
            user-select: none;
            -webkit-user-select: none;
            overflow: hidden;
        }}

        .hud-image-container {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }}

        .hud-image {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            transition: transform 0.1s ease-out;
            touch-action: pan-x pan-y pinch-zoom;
        }}

        .hud-top {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to bottom, rgba(0,0,0,0.95), rgba(0,0,0,0.7), transparent);
            padding: 20px 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}

        .hud-airport-info {{
            flex: 1;
        }}

        .hud-airport-name {{
            font-size: 32px;
            font-weight: 900;
            color: var(--hud-text);
            margin-bottom: 8px;
            line-height: 1.1;
        }}

        .hud-airport-code {{
            font-size: 26px;
            font-weight: 700;
            color: var(--accent-color);
            font-family: monospace;
        }}

        .hud-ctaf {{
            text-align: left;
            margin-top: 60px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }}

        .hud-ctaf-label {{
            font-size: 14px;
            font-weight: 600;
            color: var(--hud-text);
            opacity: 0.8;
            margin-bottom: 2px;
            white-space: nowrap;
        }}

        .hud-ctaf-value {{
            font-size: 40px;
            font-weight: 900;
            color: var(--hud-text);
            line-height: 1;
            white-space: nowrap;
        }}

        .hud-awos {{
            text-align: left;
            margin-top: 8px;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }}

        .hud-awos-label {{
            font-size: 14px;
            font-weight: 600;
            color: var(--hud-text);
            opacity: 0.8;
            margin-bottom: 2px;
            white-space: nowrap;
        }}

        .hud-awos-value {{
            font-size: 40px;
            font-weight: 900;
            color: var(--hud-text);
            line-height: 1;
            white-space: nowrap;
        }}

        .hud-bottom {{
            background: linear-gradient(to top, rgba(0,0,0,0.95), rgba(0,0,0,0.8), transparent);
            padding: 24px;
            display: flex;
            justify-content: space-around;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .hud-stat {{
            text-align: center;
            flex: 1;
            min-width: 100px;
        }}

        .hud-stat-label {{
            font-size: 14px;
            font-weight: 600;
            color: var(--hud-text);
            opacity: 0.8;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .hud-stat-value {{
            font-size: 28px;
            font-weight: 800;
            color: var(--hud-text);
            line-height: 1.1;
        }}

        .hud-close {{
            position: absolute;
            top: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            background-color: rgba(255,255,255,0.2);
            border: 2px solid white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 1001;
            font-size: 28px;
            color: white;
            font-weight: bold;
        }}

        .hud-close:hover {{
            background-color: rgba(255,255,255,0.3);
        }}

        @media (max-width: 768px) {{
            .title {{
                font-size: 28px;
            }}

            .search-input {{
                padding: 14px 16px;
                font-size: 16px;
            }}

            .sort-btn {{
                padding: 14px 20px;
                font-size: 14px;
            }}

            .airfield-card {{
                padding: 16px;
            }}

            .airfield-code {{
                font-size: 24px;
            }}

            .airfield-name {{
                font-size: 20px;
            }}

            .hud-airport-name {{
                font-size: 28px;
            }}

            .hud-airport-code {{
                font-size: 22px;
            }}

            .hud-ctaf-value {{
                font-size: 44px;
            }}

            .hud-stat-value {{
                font-size: 24px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">Airfield Directory</h1>
            <p class="subtitle">WSDOT Airport Charts - Offline Access</p>
        </div>

        <div class="search-container">
            <input type="text" class="search-input" id="searchInput" placeholder="Search by FAA code or name...">
        </div>

        <div class="sort-controls">
            <button class="sort-btn active" id="sortByName">Sort Alphabetically</button>
            <button class="sort-btn" id="sortByDistance">Sort by Distance</button>
        </div>

        <div class="airfield-list" id="airfieldList">
'''

    for airfield in airfields:
        lat = airfield.get('latitude', 'null')
        lon = airfield.get('longitude', 'null')
        image_data = airfield.get('image_base64', '')
        
        html_content += f'''        <div class="airfield-card" 
             data-code="{airfield['code'].lower()}" 
             data-name="{airfield['name'].lower()}" 
             data-lat="{lat}" 
             data-lon="{lon}"
             data-image="{image_data}"
             data-ctaf="{airfield.get('ctaf', 'N/A')}"
             data-awos="{airfield.get('awos', 'N/A')}"
             data-elev="{airfield.get('elevation', 'N/A')}"
             data-rwy-dir="{airfield.get('runway_dir', 'N/A')}"
             data-rwy="{airfield.get('length', 'N/A')}'x{airfield.get('width', 'N/A')}'"
             data-tpa="{airfield.get('tpa', 'N/A')}"
             data-full-name="{airfield['name']}"
             data-full-code="{airfield['code']}">
            <div class="airfield-header">
                <div class="airfield-code">{airfield['code']}</div>
                <div class="airfield-name">{airfield['name']}</div>
            </div>
            <div class="airfield-details">
                <div class="detail-item">Rwy: <span>{airfield.get('runway_dir', 'N/A')}</span></div>
                <div class="detail-item">Length: <span>{airfield.get('length', 'N/A')}'</span></div>
                <div class="detail-item">Width: <span>{airfield.get('width', 'N/A')}'</span></div>
                <div class="detail-item">Elev: <span>{airfield.get('elevation', 'N/A')}'</span></div>
                <div class="detail-item">CTAF: <span>{airfield.get('ctaf', 'N/A')}</span></div>
                <div class="detail-item">AWOS: <span>{airfield.get('awos', 'N/A')}</span></div>
            </div>
            <div class="distance-badge">--</div>
        </div>
'''

    html_content += '''        </div>
    </div>

    <!-- HUD Overlay -->
    <div class="hud-overlay" id="hudOverlay">
        <div class="hud-close" id="hudClose">×</div>
        <div class="hud-background" id="hudBackground">
            <div class="hud-image-container" id="hudImageContainer">
                <img class="hud-image" id="hudImage" src="" alt="Runway Diagram">
            </div>
            <div class="hud-top">
                <div class="hud-airport-info">
                    <div class="hud-airport-name" id="hudAirportName"></div>
                    <div class="hud-airport-code" id="hudAirportCode"></div>
                </div>
                <div class="hud-ctaf">
                    <div class="hud-ctaf-label">CTAF</div>
                    <div class="hud-ctaf-value" id="hudCtafValue"></div>
                </div>
                <div class="hud-awos">
                    <div class="hud-awos-label">AWOS</div>
                    <div class="hud-awos-value" id="hudAwosValue"></div>
                </div>
            </div>
        </div>
        <div class="hud-bottom">
            <div class="hud-stat">
                <div class="hud-stat-label">Elevation</div>
                <div class="hud-stat-value" id="hudElevValue"></div>
            </div>
            <div class="hud-stat">
                <div class="hud-stat-label">Runway</div>
                <div class="hud-stat-value" id="hudRwyValue"></div>
            </div>
            <div class="hud-stat">
                <div class="hud-stat-label">Length</div>
                <div class="hud-stat-value" id="hudLengthValue"></div>
            </div>
            <div class="hud-stat">
                <div class="hud-stat-label">Width</div>
                <div class="hud-stat-value" id="hudWidthValue"></div>
            </div>
            <div class="hud-stat">
                <div class="hud-stat-label">TPA</div>
                <div class="hud-stat-value" id="hudTpaValue"></div>
            </div>
        </div>
    </div>

    <script>
        const searchInput = document.getElementById('searchInput');
        const airfieldCards = document.querySelectorAll('.airfield-card');
        const sortByDistanceBtn = document.getElementById('sortByDistance');
        const sortByNameBtn = document.getElementById('sortByName');
        const hudOverlay = document.getElementById('hudOverlay');
        const hudClose = document.getElementById('hudClose');
        const hudBackground = document.getElementById('hudBackground');
        const hudImage = document.getElementById('hudImage');
        const hudImageContainer = document.getElementById('hudImageContainer');
        const hudAirportName = document.getElementById('hudAirportName');
        const hudAirportCode = document.getElementById('hudAirportCode');
        const hudCtafValue = document.getElementById('hudCtafValue');
        const hudElevValue = document.getElementById('hudElevValue');
        const hudRwyValue = document.getElementById('hudRwyValue');
        const hudTpaValue = document.getElementById('hudTpaValue');
        let userLocation = null;

        // Touch gesture state
        let scale = 1;
        let panning = false;
        let pointX = 0;
        let pointY = 0;
        let startX = 0;
        let startY = 0;

        // HUD Overlay Functions
        function openHud(card) {
            const image = card.dataset.image;
            const name = card.dataset.fullName;
            const code = card.dataset.fullCode;
            const ctaf = card.dataset.ctaf;
            const awos = card.dataset.awos;
            const elev = card.dataset.elev;
            const rwyDir = card.dataset.rwyDir;
            const rwy = card.dataset.rwy;
            const tpa = card.dataset.tpa;

            if (image) {
                hudImage.src = image;
            }
            hudAirportName.textContent = name;
            hudAirportCode.textContent = code;
            hudCtafValue.textContent = ctaf;
            hudAwosValue.textContent = awos === 'N/A' ? '' : awos;
            hudElevValue.textContent = elev + "'";
            hudRwyValue.textContent = rwyDir;
            hudLengthValue.textContent = rwy.split('x')[0] + "'";
            hudWidthValue.textContent = rwy.split('x')[1] + "'";
            hudTpaValue.textContent = tpa + "'";
            hudOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Reset touch state
            scale = 1;
            pointX = 0;
            pointY = 0;
            updateTransform();
        }

        function closeHud() {
            hudOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }

        function updateTransform() {
            hudImage.style.transform = `translate(${pointX}px, ${pointY}px) scale(${scale})`;
        }

        // Touch gesture handlers for pinch-to-zoom and pan
        hudImageContainer.addEventListener('touchstart', function(e) {
            if (e.touches.length === 1) {
                panning = true;
                startX = e.touches[0].clientX - pointX;
                startY = e.touches[0].clientY - pointY;
            } else if (e.touches.length === 2) {
                panning = false;
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                const distance = Math.sqrt(dx * dx + dy * dy);
                hudImageContainer.dataset.initialDistance = distance;
                hudImageContainer.dataset.initialScale = scale;
            }
        });

        hudImageContainer.addEventListener('touchmove', function(e) {
            e.preventDefault();
            if (e.touches.length === 1 && panning) {
                pointX = e.touches[0].clientX - startX;
                pointY = e.touches[0].clientY - startY;
                updateTransform();
            } else if (e.touches.length === 2) {
                const dx = e.touches[0].clientX - e.touches[1].clientX;
                const dy = e.touches[0].clientY - e.touches[1].clientY;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const initialDistance = parseFloat(hudImageContainer.dataset.initialDistance);
                const initialScale = parseFloat(hudImageContainer.dataset.initialScale);
                const newScale = initialScale * (distance / initialDistance);
                scale = Math.min(Math.max(newScale, 0.5), 5);
                updateTransform();
            }
        });

        hudImageContainer.addEventListener('touchend', function(e) {
            if (e.touches.length === 0) {
                panning = false;
            }
        });

        // Double-tap to reset zoom
        hudImageContainer.addEventListener('dblclick', function() {
            scale = 1;
            pointX = 0;
            pointY = 0;
            updateTransform();
        });

        hudClose.addEventListener('click', closeHud);
        hudOverlay.addEventListener('click', (e) => {
            if (e.target === hudOverlay) {
                closeHud();
            }
        });

        // Add click handlers to cards
        airfieldCards.forEach(card => {
            card.addEventListener('click', () => openHud(card));
        });

        // Haversine formula to calculate distance between two coordinates
        function calculateDistance(lat1, lon1, lat2, lon2) {
            const R = 3959; // Earth's radius in miles
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                      Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            return R * c;
        }

        // Get user's current location
        function getUserLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        userLocation = {
                            lat: position.coords.latitude,
                            lon: position.coords.longitude
                        };
                        console.log('Location obtained:', userLocation);
                        calculateDistances();
                        sortByDistance();
                    },
                    (error) => {
                        console.error('Error getting location:', error);
                        let errorMsg = 'Unable to get your location. ';
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                errorMsg += 'Location permission denied. Please enable location services in Settings.';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMsg += 'Location information unavailable.';
                                break;
                            case error.TIMEOUT:
                                errorMsg += 'Location request timed out.';
                                break;
                            default:
                                errorMsg += 'Please enable location services.';
                        }
                        alert(errorMsg);
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            } else {
                alert('Geolocation is not supported by your browser.');
            }
        }

        // Calculate distances for all airfields
        function calculateDistances() {
            airfieldCards.forEach(card => {
                const lat = parseFloat(card.dataset.lat);
                const lon = parseFloat(card.dataset.lon);
                
                if (!isNaN(lat) && !isNaN(lon) && userLocation) {
                    const distance = calculateDistance(userLocation.lat, userLocation.lon, lat, lon);
                    const badge = card.querySelector('.distance-badge');
                    if (badge) {
                        badge.textContent = distance.toFixed(1) + ' mi';
                        card.dataset.distance = distance;
                    }
                }
            });
        }

        // Sort by distance
        function sortByDistance() {
            if (!userLocation) {
                getUserLocation();
                return;
            }
            
            const cards = Array.from(airfieldCards);
            cards.sort((a, b) => {
                const distA = parseFloat(a.dataset.distance) || Infinity;
                const distB = parseFloat(b.dataset.distance) || Infinity;
                return distA - distB;
            });
            
            const list = document.getElementById('airfieldList');
            cards.forEach(card => list.appendChild(card));
            
            sortByDistanceBtn.classList.add('active');
            sortByNameBtn.classList.remove('active');
        }

        // Sort by name (alphabetical)
        function sortByName() {
            const cards = Array.from(airfieldCards);
            cards.sort((a, b) => {
                const nameA = a.dataset.name;
                const nameB = b.dataset.name;
                return nameA.localeCompare(nameB);
            });
            
            const list = document.getElementById('airfieldList');
            cards.forEach(card => list.appendChild(card));
            
            sortByNameBtn.classList.add('active');
            sortByDistanceBtn.classList.remove('active');
        }

        // Event listeners
        sortByDistanceBtn.addEventListener('click', sortByDistance);
        sortByNameBtn.addEventListener('click', sortByName);

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            
            airfieldCards.forEach(card => {
                const code = card.dataset.code;
                const name = card.dataset.name;
                
                if (code.includes(query) || name.includes(query)) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    </script>
</body>
</html>'''

    # Write to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Generate manifest.json
    manifest_content = '''{
  "name": "Airfield Directory",
  "short_name": "Airfields",
  "description": "Offline WSDOT Airfield Directory with runway diagrams and CTAF frequencies",
  "start_url": "./index.html",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#000000",
  "orientation": "portrait",
  "scope": "./"
}'''
    
    with open('manifest.json', 'w', encoding='utf-8') as f:
        f.write(manifest_content)
    
    # Generate sw.js (Service Worker)
    sw_content = '''const CACHE_NAME = 'airfield-directory-v1';
const urlsToCache = [
  './',
  './index.html',
  './manifest.json'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});'''
    
    with open('sw.js', 'w', encoding='utf-8') as f:
        f.write(sw_content)
    
    # Generate map.html
    map_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Airfield Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        #map {
            height: 100vh;
            width: 100%;
        }
        .custom-marker {
            background: #e63946;
            border: 3px solid #fff;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        .popup-content {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .popup-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .popup-code {
            font-size: 24px;
            font-weight: 900;
            color: #0066cc;
            font-family: monospace;
        }
        .popup-name {
            font-size: 20px;
            font-weight: 700;
            color: #000;
        }
        .popup-image {
            width: 100%;
            height: auto;
            border-radius: 8px;
            margin-bottom: 12px;
            border: 2px solid #000;
        }
        .popup-details {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 14px;
            color: #333;
        }
        .popup-detail-item {
            font-weight: 500;
        }
        .popup-detail-item span {
            font-weight: 700;
            color: #000;
        }
    </style>
</head>
<body>
    <div id="map"></div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const airfields = [
'''
    
    for airfield in airfields:
        lat = airfield.get('latitude')
        lon = airfield.get('longitude')
        code = airfield.get('code', 'UNK')
        name = airfield.get('name', 'Unknown')
        image = airfield.get('image_base64', '')
        ctaf = airfield.get('ctaf', 'N/A')
        awos = airfield.get('awos', 'N/A')
        elev = airfield.get('elevation', 'N/A')
        rwy_dir = airfield.get('runway_dir', 'N/A')
        length = airfield.get('length', 'N/A')
        width = airfield.get('width', 'N/A')
        tpa = airfield.get('tpa', 'N/A')
        
        if lat is not None and lon is not None:
            map_html += f'            {{ lat: {lat}, lon: {lon}, code: "{code}", name: "{name}", image: "{image}", ctaf: "{ctaf}", awos: "{awos}", elev: "{elev}", rwy_dir: "{rwy_dir}", length: "{length}", width: "{width}", tpa: "{tpa}" }},\n'
    
    map_html = map_html.rstrip(',\n') + '\n'
    
    map_html += '''        ];
        
        // Initialize map centered on Washington state
        const map = L.map('map').setView([47.5, -120.5], 7);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        
        // Add markers for each airfield
        airfields.forEach(airfield => {
            const marker = L.circleMarker([airfield.lat, airfield.lon], {
                radius: 8,
                fillColor: '#e63946',
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
            
            // Add tooltip on hover
            marker.bindTooltip(`<b>${airfield.code}</b><br>${airfield.name}`, {
                permanent: false,
                direction: 'top',
                offset: [0, -10]
            });
            
            // Add popup on click with detailed information
            const popupContent = `
                <div class="popup-content">
                    <div class="popup-header">
                        <div class="popup-code">${airfield.code}</div>
                        <div class="popup-name">${airfield.name}</div>
                    </div>
                    ${airfield.image ? `<img src="${airfield.image}" class="popup-image" alt="${airfield.name}">` : ''}
                    <div class="popup-details">
                        <div class="popup-detail-item">Rwy: <span>${airfield.rwy_dir}</span></div>
                        <div class="popup-detail-item">Length: <span>${airfield.length}'</span></div>
                        <div class="popup-detail-item">Width: <span>${airfield.width}'</span></div>
                        <div class="popup-detail-item">Elev: <span>${airfield.elev}'</span></div>
                        <div class="popup-detail-item">CTAF: <span>${airfield.ctaf}</span></div>
                        <div class="popup-detail-item">AWOS: <span>${airfield.awos}</span></div>
                    </div>
                </div>
            `;
            marker.bindPopup(popupContent, { maxWidth: 400 });
        });
    </script>
</body>
</html>'''
    
    with open('map.html', 'w', encoding='utf-8') as f:
        f.write(map_html)
    
    print(f"Generated PWA package with {len(airfields)} airfields:")
    print(f"  - index.html (with embedded Base64 images)")
    print(f"  - manifest.json (PWA configuration)")
    print(f"  - sw.js (Service Worker for offline caching)")
    print(f"  - map.html (Interactive airfield map)")
    print(f"\nUpload all three files to iCloud Drive for offline PWA functionality")

if __name__ == '__main__':
    generate_html()
