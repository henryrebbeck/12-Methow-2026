import os
import urllib.request
import urllib.error

# Directory for Washington airport PDFs
output_dir = 'Washington Airfield PDFs'

# Corrected URLs for failed airports
corrected_airports = {
    "Arlington": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/Arlington.pdf",
    "AmericanLake": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/AmericanLake.pdf",
    "CamanoIsland": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/CamanoIsland.pdf",
    "Cashmere-Dryden": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/Cashmere-Dryden.pdf",
    "Chehalis-Centralia": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/Chehalis-Centralia.pdf",
    "Chewelah": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/Chewelah.pdf",
    "CleElum": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/CleElum.pdf",
    "Columbia": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/Columbia.pdf"
}

# Download PDFs with corrected URLs
success_count = 0
fail_count = 0
failed_airports = []

for airport, url in corrected_airports.items():
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
