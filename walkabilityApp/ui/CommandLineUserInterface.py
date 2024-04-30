from walkabilityApp.processor.Processor import Processor
class CommandLineUserInterface:
    # instance methods:
    def start(self):
        stop = False
        while (not stop):
            print("Enter gps coordinates: ")
            coordinates = input()
            try:
                print(self.obtain_result(gps_coordinates=coordinates))
            except:
                print("Invalid input. Please enter gps coordinates.")
            print("Would you like to run another search (y/n)?")
            again = input().strip()
            if (again[0] == 'n'):
                stop = True

    def obtain_result(self, gps_coordinates):
        processor = Processor(gps_coordinates)
        return processor.process_location()