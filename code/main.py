from pathlib import Path
from tqdm import tqdm
from extraction.extraction import extract_metadata
from generation.generation import generate_metadata

import requests
import argparse
import json
import os

PROMPTS_DIR = Path(__file__).parent / "generation/prompts"
INPUTS_DIR = Path(__file__).parent.parent / "data/inputs"
OUTPUTS_DIR = Path(__file__).parent.parent / "data/outputs"

API_KEY = os.environ.get("OPENAI_API_KEY")
GEONAMES_USERNAME = os.environ.get("GEONAMES_USERNAME")

BASE_API = "http://api.geonames.org/"
BASE_URL = "https://www.geonames.org/"

assert API_KEY, "OPENAI_API_KEY environment variable must be set."
assert GEONAMES_USERNAME, "GEONAMES_USERNAME environment variable must be set."

def get_geonames_urls(spatial_value):
    geonames_urls = []
    for place in spatial_value:
        params = {
            'q': place,
            'maxRows': 1,
            'username': GEONAMES_USERNAME,
            'type': 'json'
        }

        response = requests.get(f"{BASE_API}searchJSON", params=params)
        if response.status_code == 200:
            data = response.json()
            if 'geonames' in data:
                if len(data['geonames']) > 0:
                    for geo in data['geonames']:
                        url = f"{BASE_URL}{geo.get('geonameId')}"
                        geonames_urls.append(url)
                else:
                    geonames_urls.append(place)  # If no match found, keep original place name
        # else:
            # print(f"   - Error fetching data from GeoNames: {response.status_code}")
    return geonames_urls

def main():
    print("Starting process...")
    parser = argparse.ArgumentParser(description='Process Data')
    parser.add_argument('-l', '--language', default='spa',
                        choices=['spa', 'eng'],
                        help='Dataset language to process (default: spa)')
    
    language = parser.parse_args().language
    # print(f"Selected language: {language}")

    files_path = INPUTS_DIR / language
    for filename in tqdm(os.listdir(files_path)):
        output_file = OUTPUTS_DIR / language / f"{Path(filename).stem}.json"
        if output_file.exists():
            print(f"Skipping {filename}, output already exists.")
            continue
        # print(filename)
        file_path = files_path / filename
        mapped_metadata = extract_metadata(file_path)
        generated_metadata = generate_metadata(file_path, PROMPTS_DIR, API_KEY)

        all_metadata = {**mapped_metadata, **generated_metadata}
        # print(f"All Metadata for {filename}: {json.dumps(all_metadata, ensure_ascii=False, indent=4)}")

        # Special Case: 'dct:spatial'
        if 'dct:spatial' in all_metadata:
            spatial_value = all_metadata['dct:spatial']
            geonames_urls = get_geonames_urls(spatial_value)
            if len(geonames_urls) > 0:
                all_metadata['dct:spatial'] = geonames_urls
            #print(f"All FINAL Metadata for {filename}: {json.dumps(all_metadata, ensure_ascii=False, indent=4)}")
        
        os.makedirs(output_file.parent, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()