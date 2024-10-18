# Walkability Navigator
Walkable cities offer a multitude of benefits for both individuals and communities. By fostering a pedestrian-friendly environment, these cities contribute to various aspects of well-being, including physical and mental health, environmental sustainability, economic prosperity, social interaction, and safety. The emphasis on walkability enhances the overall quality of life for residents, creating a cohesive and thriving community.

Walkability Navigator was created to help users navigate the stresses of moving to a new location. Users may enter the gps coordinates of a potential new apartment or home and will be delivered a walkability score to help them through their decision-making process. Additionally users may create an account and save their favorite options in a dashboard.

## Design
Utilizes a 3-tier archictecture with the code split into the following packages: ui, datamanagement and processor.

Fetches data from googlemaps api & evaluates the walkability of a location based on the location's proximity to amenities.

## Images of Site
### Homepage
![homepage screenshot](https://github.com/psterritt5/walkability/blob/63b1cb8bf196d08826524d03786d296ec0408647/walkabilityApp/images/homepage.png)

### Result page
![result page screenshot](https://github.com/psterritt5/walkability/blob/63b1cb8bf196d08826524d03786d296ec0408647/walkabilityApp/images/result.png)

### Dashboard
![dashboard screenshot](https://github.com/psterritt5/walkability/blob/63b1cb8bf196d08826524d03786d296ec0408647/walkabilityApp/images/dashboard-view.png)

## Steps to run
1. If you do not already have a google developer account, you will need to create one [here](https://developers.google.com/).
2. [From the google developers page]((https://developers.google.com/)), create a new project and enable the places API.
3. Next grab your API Key and paste it into 'MAPS_API.txt' 
4. Compile program and run in command line or browser.
5. To run in browser: run 'app.py' and follow link in command line to run on local device.
6. To run in command line: run 'main.py'.
