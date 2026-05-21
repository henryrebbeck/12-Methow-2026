import os
import urllib.request
import urllib.error

# Directory for Washington airport PDFs
output_dir = 'Washington Airfield PDFs'

# Remaining airport URLs
remaining_airports = {
    "DesertAire": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/DesertAire.pdf",
    "EdCarlson": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/EdCarlson.pdf",
    "Fishermans": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/Fishermans.pdf",
    "Goldendale": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/Goldendale.pdf",
    "GrantCountyInt": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/GrantCountyInt.pdf",
    "LakeWenatchee": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/LakeWenatchee.pdf",
    "LowerGraniteState": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/LowerGraniteState.pdf",
    "LowerMonumentalState": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/LowerMonumentalState.pdf",
    "PierceCounty-ThunField": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/PierceCounty-ThunField.pdf",
    "PortofIlwaco": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/PortofIlwaco.pdf",
    "PortofPoulsbo": "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/PortofPoulsbo.pdf"
}

# Download PDFs
success_count = 0
fail_count = 0
failed_airports = []

for airport, url in remaining_airports.items():
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
