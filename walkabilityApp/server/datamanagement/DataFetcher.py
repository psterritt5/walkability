import googlemaps
class DataFetcher:
    # Static variables for performing a search
    # Per API radius = dist in meters, 200meters = 0.125miles however testing showed places within ~0.5 miles
    RADIUS = 200  # search radius ~0.5 miles
    # keywords
    GROCERY = ['grocery_store']
    EAT_OUT = ['cafe', 'bakery', 'restaurant', 'bar']
    PUBLIC_TRANSIT = ['subway_station', 'bus_stop']
    HEALTH_AND_WELLBEING = ['park', 'gym', 'pharmacy', 'library', 'community_garden']

    CATEGORIES = [GROCERY, EAT_OUT, PUBLIC_TRANSIT, HEALTH_AND_WELLBEING]
    CATEGORY_NAMES = ['grocery', 'eat_out', 'public_transit', 'health_and_well_being']

    # Constructor
    def __init__(self, gps_coordinates):
        self.gps_coordinates = gps_coordinates
        self.dict_results = dict.fromkeys(DataFetcher.CATEGORY_NAMES) # keys = category names, values = set of destinations (string)

    # Instance Methods:
    '''
    This is the main access point outside of this class. The method fetches data from googlemaps api and
    returns a dictionary of search results split by the keys from the static var CATEGORY_NAMES
    '''
    def perform_search(self):
        API_KEY = open('MAPS_API.txt', 'r').read()
        map_client = googlemaps.Client(key=API_KEY)

        # perform search on each category and add results to a set to ensure no duplicates are added
        for i in range(len(DataFetcher.CATEGORIES)):
            self.dict_results[DataFetcher.CATEGORY_NAMES[i]] = set()
            # call helper function to store each unique results
            self.fetch_all_keywords_for_category(index=i, map_client=map_client)
        return self.dict_results

    '''
        Helper method which iterates over each keyword for a given category, invokes make_api_request()
        and stores the results of the search in dict_results
    '''
    def fetch_all_keywords_for_category(self, index, map_client):
        for keyword in DataFetcher.CATEGORIES[index]:
            places = self.make_api_request(map_client=map_client, keyword=keyword)
            for place in places.get('results', []):
                # Add the name to the set for the category
                self.dict_results[DataFetcher.CATEGORY_NAMES[index]].add(
                    str(place.get('name', 'N/A')))  # + place.get('vicinity', 'N/A')))

    '''
    Helper method which performs an individual api request for a given keyword.
    '''
    def make_api_request(self, map_client, keyword):
        # Perform search on keyword and add results to dict key=category, value = str(name of buisness)
        # Values stored in a set to ensure no duplicates are added
        places = map_client.places_nearby(location=self.gps_coordinates, radius=DataFetcher.RADIUS, open_now=False,
                                          keyword=keyword)
        return places
