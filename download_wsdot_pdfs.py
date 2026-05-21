import os
import urllib.request
import urllib.error

# Create new directory for Washington airport PDFs
output_dir = 'Washington Airfield PDFs'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Base URL for WSDOT airport PDFs
base_url = "https://wsdot.wa.gov/publications/manuals/fulltext/M3049/"

# List of airport names (from WSDOT site)
airports = [
    "AmericanLakeSPB",
    "Anacortes",
    "AndersonField",
    "Apex",
    "ArlingtonMunicipal",
    "AuburnMunicipal",
    "AveyField",
    "BanderaState",
    "BellinghamInternational",
    "BoeingField",
    "BowermanField",
    "BowersField",
    "BremertonNational",
    "CamanoIslandAirfield",
    "CashmereDryden",
    "CedarsNorth",
    "ChehalisCentralia",
    "ChewelahMunicipal",
    "CleElumMunicipal",
    "ColumbiaGorgeRegional",
    "ColvilleMunicipal",
    "CopalisState",
    "DarringtonMunicipal",
    "DavenportMunicipal",
    "DeLaurentis",
    "DeVere",
    "DeerParkMunicipal",
    "DesertAireRegional",
    "DorothyScott",
    "EastonState",
    "EdCarlsonMemorial",
    "EphrataMunicipal",
    "FeltsField",
    "FerryCounty",
    "FirstAirField",
    "FishermansBay",
    "FloathavenSPB",
    "FlyForFun",
    "ForksMunicipal",
    "FridayHarbor",
    "FridayHarborSPB",
    "Goheen",
    "GoldendaleMunicipal",
    "GrandCouleeDam",
    "GrantCountyInternational",
    "GroveField",
    "HarveyField",
    "HoskinsField",
    "IoneMunicipal",
    "JeffersonCounty",
    "KenmoreAirHarbor",
    "LakeChelan",
    "LakeWenatcheeState",
    "LindMunicipal",
    "LittleGoose",
    "LopezIsland",
    "LostRiver",
    "LowerGranite",
    "LowerMonumental",
    "LyndenMunicipal",
    "Mansfield",
    "MartinField",
    "MeadFlyingService",
    "MearsField",
    "MethowValleyState",
    "MosesLakeMunicipal",
    "NormanGrierField",
    "OceanShoresMunicipal",
    "OdessaMunicipal",
    "OlympiaRegional",
    "OmakMunicipal",
    "OrcasIsland",
    "OthelloMunicipal",
    "Packwood",
    "PangbornMemorial",
    "PearsonField",
    "PierceCounty",
    "PointRoberts",
    "PortAngelesSPB",
    "PortIlwaco",
    "PortPoulsbo",
    "PortWhitman",
    "Prosser",
    "PruField",
    "PullmanMoscow",
    "Quillayute",
    "QuincyMunicipal",
    "RandKSkyranch",
    "RangerCreekState",
    "RentonMunicipal",
    "Richland",
    "RocheHarborSPB",
    "RogersburgState",
    "RosaliaMunicipal",
    "RosarioSPB"
]

# Download PDFs
success_count = 0
fail_count = 0
failed_airports = []

for airport in airports:
    url = f"{base_url}{airport}.pdf"
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
