import googlemaps
import os
from flask import current_app
import requests
import time

class DataFetcher:
    # Static variables for performing a search
    RADIUS = 600  # search radius ~0.37 miles (about a 7-8 minute walk)
    
    # Define valid types for each category
    VALID_TYPES = {
        'grocery': {'grocery_or_supermarket', 'supermarket', 'grocery_store'},
        'eat_out': {'restaurant', 'cafe', 'bakery', 'bar', 'food'},
        'public_transit': {'subway_station', 'bus_station', 'train_station', 'transit_station'},
        'health_and_well_being': {'park', 'gym', 'health', 'pharmacy', 'doctor', 'hospital'}
    }
    
    # Search parameters for each category - optimized to reduce API calls
    CATEGORIES = {
        'grocery': ['grocery_or_supermarket'],  # Combined search
        'eat_out': ['restaurant'],  # Main type that includes most food places
        'public_transit': ['transit_station'],  # Generic type that includes all transit
        'health_and_well_being': ['health', 'park']  # Split into two main groups
    }
    
    CATEGORY_NAMES = ['grocery', 'eat_out', 'public_transit', 'health_and_well_being']

    def __init__(self, address):
        """Initialize the data fetcher with an address."""
        if not address or not isinstance(address, str):
            raise ValueError("Address must be a non-empty string")
        
        self.address = address.strip()
        self.gps_coordinates = None
        self.dict_results = {name: set() for name in self.CATEGORY_NAMES}
        self.place_details = {}  # Store place details to prevent duplicates
        
    def geocode_address(self, map_client):
        """Convert address to GPS coordinates"""
        try:
            if not self.address:
                print("Error: Empty address")
                return False
                
            geocode_result = map_client.geocode(self.address)
            if not geocode_result:
                print("Error: No geocoding results found")
                return False
                
            location = geocode_result[0].get('geometry', {}).get('location')
            if not location or 'lat' not in location or 'lng' not in location:
                print("Error: Invalid location format in geocoding results")
                return False
                
            self.gps_coordinates = (float(location['lat']), float(location['lng']))
            print(f"Successfully geocoded address to coordinates: {self.gps_coordinates}")
            return True
        except Exception as e:
            print(f"Geocoding error: {str(e)}")
            return False

    def perform_search(self):
        """Main method to perform the search"""
        try:
            api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
            if not api_key:
                raise ValueError("Google Maps API key not found in configuration")
                
            map_client = googlemaps.Client(key=api_key)
            
            if not self.geocode_address(map_client):
                raise ValueError("Could not geocode the provided address")
            
            # Make parallel requests for each main category
            for category_name, types in self.CATEGORIES.items():
                try:
                    self.make_api_request(types[0], category_name)
                    # Only add a tiny delay between major category searches
                    if len(types) > 1:
                        time.sleep(0.05)  # Reduced delay
                        self.make_api_request(types[1], category_name)
                except Exception as e:
                    print(f"Error searching for {category_name}: {str(e)}")
                    continue
            
            return self.dict_results
        except Exception as e:
            print(f"Search error: {str(e)}")
            raise

    def make_api_request(self, type_keyword, category_name):
        """Make a single API request for a type."""
        try:
            if not self.gps_coordinates:
                print(f"Error: No GPS coordinates available for API request ({type_keyword})")
                return
                
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{self.gps_coordinates[0]},{self.gps_coordinates[1]}",
                "radius": self.RADIUS,
                "key": current_app.config['GOOGLE_MAPS_API_KEY'],
                "type": type_keyword  # Use type instead of keyword for better categorization
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["status"] == "OK":
                for result in data.get("results", []):
                    place_id = result.get("place_id")
                    place_name = result.get("name")
                    place_types = set(result.get("types", []))
                    location = result.get("geometry", {}).get("location", {})
                    
                    # Check if any of the place's types match our valid types for this category
                    if place_id and place_name and (place_types & self.VALID_TYPES[category_name]):
                        # Only add if we haven't seen this place before
                        if place_id not in self.place_details:
                            self.place_details[place_id] = {
                                'name': place_name,
                                'types': place_types,
                                'categories': set(),
                                'location': location
                            }
                            
                            # Add to category if not already there
                            if category_name not in self.place_details[place_id]['categories']:
                                self.place_details[place_id]['categories'].add(category_name)
                                self.dict_results[category_name].add(place_name)
                                print(f"Added {place_name} to {category_name}")
            else:
                print(f"API request failed for {type_keyword} with status: {data['status']}")
                    
        except Exception as e:
            print(f"API request error for {type_keyword}: {str(e)}")
            # Don't raise the exception, just log it and continue with other types

    def get_places_by_category(self):
        """Return a dictionary of places grouped by category."""
        return self.dict_results
