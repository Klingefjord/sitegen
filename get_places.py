import googlemaps
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

# Function to search for places with pagination
def search_places(query, location, radius):
    places_result = gmaps.places_nearby(location=location, radius=radius, keyword=query)
    all_places = places_result.get('results', [])
    
    # Handle pagination
    while 'next_page_token' in places_result:
        # Google API requires a short delay before next request using the next_page_token
        time.sleep(2)
        places_result = gmaps.places_nearby(page_token=places_result['next_page_token'])
        all_places.extend(places_result.get('results', []))
    
    return all_places

# Function to get detailed information about a place
def get_place_details(place_id):
    details = gmaps.place(place_id=place_id, fields=['name', 'formatted_address', 'opening_hours', 'formatted_phone_number', 'website'])
    return details.get('result', {})

# Function to filter places based on criteria
def filter_places(places):
    filtered_places = []
    for place in places:
        details = get_place_details(place['place_id'])
        if all(key in details for key in ('name', 'formatted_address', 'opening_hours', 'formatted_phone_number')):
            if 'website' not in details:
                filtered_places.append({
                    'place_id': place['place_id'],
                    'name': details['name'],
                    'address': details['formatted_address'],
                    'opening_hours': details['opening_hours'],
                    'phone_number': details['formatted_phone_number']
                })
    return filtered_places

# Example usage
def main():
    # Search parameters
    query = 'cafe'
    location = '52.515040, 13.405683'  # Berlin, Germany
    radius = 10_000  # 10 km

    # Search for places
    places = search_places(query, location, radius)
    print("Found {} places".format(len(places)))
    # Filter places based on criteria
    filtered_places = filter_places(places)
    print("Filtered down to {} places".format(len(filtered_places)))
    
    # Save the filtered places to a JSON file
    with open('places.json', 'w') as f:
        json.dump(filtered_places, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
