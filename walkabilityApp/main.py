import time
import googlemaps

def make_api_request(map_client, gps_coordinates, radius, keyword):

    # Perform search on keyword and add results to dict key=category, value = str(name of buisness)
    # Values stored in a set to ensure no duplicates are added
    places = map_client.places_nearby(
        location=gps_coordinates,
        radius=radius,
        open_now = False,
        keyword = keyword,
    )
    return places
def store_unique_results(gps_coordinates, radius, categories, category_names, dict_results):
    API_KEY = open('MAPS_API.txt', 'r').read()
    map_client = googlemaps.Client(key=API_KEY)

    # perform search on each keyword and add results to a set to ensure no duplicates are added
    for i in range(len(categories)):
        #time.sleep(1) # Delay required by API to allow new request to be delivered
        dict_results[category_names[i]] = set()
        for keyword in categories[i]:
            places = make_api_request(map_client=map_client,gps_coordinates=gps_coordinates,radius=radius, keyword=keyword)
            for place in places.get('results', []):
                # Add the name to the set for the category
                dict_results[category_names[i]].add(str(place.get('name', 'N/A')))  # + place.get('vicinity', 'N/A')))

def perform_search(gps_coordinates):
    # First define criteria for search
    # search radius ~0.5 miles
    # Per API radius = dist in meters, 200meters = 0.125miles however testing showed places within ~0.5 miles
    radius = 200
    #keywords
    grocery = ['grocery_store']
    eat_out = ['cafe', 'bakery', 'restaurant', 'bar']
    public_transit = ['subway_station', 'bus_stop']
    health_and_well_being = ['park', 'gym', 'pharmacy', 'library', 'community_garden']

    categories = [grocery, eat_out, public_transit, health_and_well_being]
    category_names = ['grocery', 'eat_out', 'public_transit', 'health_and_well_being']
    dict_results = dict.fromkeys(category_names) # keys = category names, values = set of destinations (string)

    # call helper function to store unique results
    store_unique_results(gps_coordinates=gps_coordinates, radius=radius, categories=categories, category_names=category_names, dict_results=dict_results)

    return dict_results

def calculate_walkability_score(dict_results):
    # Walkability = sum(score x weight) for each category / sum(3* weight)
    # Weight of categories - high =3, medium=2, low=1:
    # Score of categories - great = 3, good = 2, low = 1, unacceptable = 0
    numerator = 0.0
    # High importance
    numerator += get_category_score(key='grocery', dict_results=dict_results)*3 # weight of groceries is 3
    numerator += get_category_score(key='health_and_well_being', dict_results=dict_results)*3
    # Medium importance
    numerator += get_category_score(key='eat_out', dict_results=dict_results)*2
    numerator += get_category_score(key='public_transit', dict_results=dict_results)*2
    # Low weight = 1
    # As of now none could update categories or use a user defined

    # denominator = sum(max score * weight) where max score = 3
    denominator = 3*3*2 + 3*2*2 # currently we have 2 categories with high importance and 2 with medium importance

    return numerator/denominator*10
def get_category_score(key, dict_results):
    length_value_set = len(dict_results[key])
    if(length_value_set == 0):
        return 0 #unaccetable
    elif(length_value_set < 2):
        return 1 #low
    elif (length_value_set < 4):
        return 2 #good
    else:
        return 3 # great

def interpret_score(walkability_score):
    interpretation = 'The walkability score of the provided location is: ' + str(walkability_score) + ' out of 10 which is '
    if(walkability_score < 2.5):
        interpretation+="a very low score. This area is not walkable."
    elif(walkability_score < 5):
        interpretation+="a low score. This area is not very walkable."
    elif(walkability_score < 7.5):
        interpretation+="a good score! This area is pretty walkable!"
    else:
        interpretation+="a great score! This area is very walkable!"
    return interpretation
def run(gps_coordinates):
    dict_results = perform_search(gps_coordinates=gps_coordinates)
    score = calculate_walkability_score(dict_results=dict_results)
    return interpret_score(walkability_score=score)
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    stop = False
    while (not stop):
        print("Enter gps coordinates: ")
        coordinates = input()
        try:
            print(run(gps_coordinates=coordinates))
        except:
            print("Invalid input. Please enter gps coordinates.")
        print("Would you like to run another search (y/n)?")
        again = input().strip()
        if(again[0] == 'n'):
            stop = True


    '''
    df = read_file()
    city = df.filter(items=['city'])
    city = city.sort_values(by='city')
    print(city.head(100))
    df = filter_df(df, 'Abington')
    print(df.head())
    df = align_neighborhoods(df, 'Philly_neighborhoods.csv')
    '''
'''Old code

def read_file():
    data_file = open("yelp_academic_dataset_business.json")
    data = []
    for line in data_file:
        data.append(json.loads(line))
    data_file.close()
    # return dataframe with raw yelp data
    return pd.DataFrame(data)

def filter_df(df_raw, city_name):
    # Filter df_raw to only include necessary columns
    df_city = df_raw.filter(items=['city','state','postal_code','attributes', 'categories'])
    # filter data to only include buisnesses that are open and located in the area of interest
    df_city = df_city.loc[(df_city['city'] == city_name)]
    return df_city
def align_neighborhoods(df_city, file_name):
    print(df_city.filter(items=['categories']).head(50))
    df_zipcodes = pd.read_csv(file_name)
    df_city['postal_code'] = df_city['postal_code'].astype(int)
    df_zipcodes['postal_code'] = df_zipcodes['postal_code'].astype(int)
    df_city = pd.merge(df_city,df_zipcodes,on='postal_code', how='inner')
    print(df_city.filter(items=['neighborhood', 'categories']).head(50))
    return df_city

'''