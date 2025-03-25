from datamanagement.DataFetcher import DataFetcher

class Processor:
    def __init__(self, address):
        """Initialize the processor with an address."""
        self.address = address
        self.data_fetcher = None

    def process_location(self, address):
        """Process a location and return its walkability score."""
        try:
            self.data_fetcher = DataFetcher(address)
            results = self.data_fetcher.perform_search()
            places_by_category = self.data_fetcher.get_places_by_category()
            
            score = self.calculate_walkability_score(results)
            interpretation = self.interpret_score(score, places_by_category)
            return score, interpretation
        except Exception as e:
            print(f"Error processing location: {str(e)}")
            return 0, "Error processing location"

    def calculate_walkability_score(self, results):
        """Calculate walkability score based on nearby amenities."""
        try:
            # Initialize weights for each category
            weights = {
                'grocery': 0.3,
                'eat_out': 0.2,
                'public_transit': 0.3,
                'health_and_well_being': 0.2
            }
            
            # Calculate weighted score for each category
            total_score = 0
            for category, places in results.items():
                num_places = len(places)
                # Cap the number of places to avoid inflated scores
                capped_places = min(num_places, 5)  # Cap at 5 places per category
                # Calculate category score (0-2.5 per category)
                category_score = (capped_places / 5) * weights[category] * 10
                total_score += category_score
            
            # Round to 1 decimal place
            return round(total_score, 1)
        except Exception as e:
            print(f"Error calculating score: {str(e)}")
            return 0

    def interpret_score(self, score, places_by_category):
        """Provide a detailed interpretation of the walkability score."""
        try:
            # Base interpretation
            if score >= 8:
                interpretation = "excellent walkability! Most errands can be accomplished on foot."
            elif score >= 6:
                interpretation = "very good walkability. Many amenities within walking distance."
            elif score >= 4:
                interpretation = "good walkability. Some amenities within walking distance."
            elif score >= 2:
                interpretation = "moderate walkability. Some amenities require transportation."
            else:
                interpretation = "poor walkability. Most destinations require a car or other transportation."

            # Format the full message with place names
            message = f"The walkability score for this location is {score}/10, which indicates {interpretation}\n\nNearby amenities:"
            
            # Add detailed breakdown of places by category
            for category, places in places_by_category.items():
                formatted_category = category.replace('_', ' ').title()
                message += f"\n\n{formatted_category} ({len(places)} places):"
                if places:
                    for place in sorted(places):
                        message += f"\n- {place}"
                else:
                    message += "\n- None found"
            
            return message
        except Exception as e:
            print(f"Error interpreting score: {str(e)}")
            return "Error interpreting results"