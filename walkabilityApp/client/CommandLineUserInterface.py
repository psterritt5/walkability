from walkabilityApp.processor.Processor import Processor
class CommandLineUserInterface:
    # instance methods:
    '''
    Main Access point for main. Prompts user for gps coordinates and returns the walkability result.
    '''
    def start(self):
        stop = False
        while not stop:
            print("Enter gps coordinates: ")
            coordinates = input()
            try:
                print(self.obtain_result(gps_coordinates=coordinates))
            except:
                print("Invalid input. Please enter gps coordinates.")
            print("Would you like to run another search (y/n)?")
            again = input().strip()
            if again[0] == 'n':
                stop = True
    '''
    Helper method - Takes user input of gps coordinates and attempts to obtain a walkability metric by creating an 
    instance of Processor & calling process_location(). 
    Will throw an exception if the specified location is not valid.
    '''
    def obtain_result(self, gps_coordinates):
        processor = Processor(gps_coordinates)
        return processor.process_location()