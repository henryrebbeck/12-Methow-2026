import os
import urllib.request
import urllib.error

# Directory for Washington airport PDFs
output_dir = 'Washington Airfield PDFs'

# Final airport URLs
final_airports = {
    "Skyranch": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/Skyranch.pdf",
    "Pullman-Moscow": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/Pullman-Moscow.pdf",
    "RocheHarbor": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/RocheHarbor.pdf",
    "rosario": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/rosario.pdf"
}

# Download PDFs
success_count = 0
fail_count = 0
failed_airports = []

for airport, url in final_airports.items():
    filename = f"{output_dir}/{airport}.pdf"
    
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Downloaded: {airport}.pdf")
        success_count += 1
    except urllib.error.HTTPError as e:
        print(f"Failed to download: {airport}.pdf (HTTP Error: {e.code})")
        fail_count += 1
        failed_airports.append(airport)
    except urllib.error.URLError as e:
        print(f"Failed to download: {airport}.pdf (URL Error: {e.reason})")
        fail_count += 1
        failed_airports.append(airport)
    except Exception as e:
        print(f"Error downloading {airport}.pdf: {e}")
        fail_count += 1
        failed_airports.append(airport)

print(f"\nDownload complete:")
print(f"Success: {success_count}")
print(f"Failed: {fail_count}")

if failed_airports:
    print(f"\nFailed airports:")
    for airport in failed_airports:
        print(f"  - {airport}")
