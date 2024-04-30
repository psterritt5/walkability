from walkabilityApp.datamanagement.DataFetcher import DataFetcher
class Processor:
    # Constructor
    def __init__(self, gps_coordinates):
        self.data_fetcher = DataFetcher(gps_coordinates)
    # Instance Methods
    def process_location(self):
        # Get data for specified loc w/ DataFetcher instance
        dict_results = self.data_fetcher.perform_search()
        # compute walkability score
        score = self.calculate_walkability_score(dict_results=dict_results)
        # return interpreted score
        return self.interpret_score(walkability_score=score)

    def calculate_walkability_score(self,dict_results):
        # Walkability = sum(score x weight) for each category / sum(3* weight)
        # Weight of categories - high =3, medium=2, low=1:
        # Score of categories - great = 3, good = 2, low = 1, unacceptable = 0
        numerator = 0.0
        # High importance
        numerator += self.get_category_score(key='grocery', dict_results=dict_results) * 3 # weight of groceries is 3
        numerator += self.get_category_score(key='health_and_well_being', dict_results=dict_results) * 3
        # Medium importance
        numerator += self.get_category_score(key='eat_out', dict_results=dict_results) * 2
        numerator += self.get_category_score(key='public_transit', dict_results=dict_results) * 2
        # Low weight = 1
        # As of now none could update categories or use a user defined

        # denominator = sum(max score * weight) where max score = 3
        denominator = 3*3*2 + 3*2*2 # currently we have 2 categories with high importance and 2 with medium importance

        return numerator/denominator*10

    def get_category_score(self, key, dict_results):
        length_value_set = len(dict_results[key])
        if(length_value_set == 0):
            return 0 #unaccetable
        elif(length_value_set < 2):
            return 1 #low
        elif (length_value_set < 4):
            return 2 #good
        else:
            return 3 # great

    def interpret_score(self, walkability_score):
        interpretation = 'The walkability score of the provided location is: ' + str(walkability_score) + ' out of 10 which is '
        if walkability_score < 2.5:
            interpretation+="a very low score. This area is not walkable."
        elif walkability_score < 5:
            interpretation+="a low score. This area is not very walkable."
        elif walkability_score < 7.5:
            interpretation+="a good score! This area is pretty walkable!"
        else:
            interpretation+="a great score! This area is very walkable!"
        return interpretation