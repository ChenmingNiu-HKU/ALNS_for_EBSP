## Adptive Large Neighborhood Search Algorithm for Solving Electric Bus Scheduleing Problem

The project develops an adaptive large neighborhood search algorithm to solve the electric bus scheduling problem to 
minimize the total cost of e-bus purchase, charging, labor and battery degradation.

To run the program:
- Download the folder 
- Put your own timetable (csv file) in the timetable folder
- Run main.py
- Input your own charging station capacity and the name of your timetable file

It's noted that the timetable csv file contains 3 columns:
1. StartTimeMin: int/float, i.e. 300 (5:00 AM), represents the start time of the bus task in the unit of min
2. TravelTimeMin: int/float, i.e. 90 (1.5 hours), represents the travel time of the bus task in the unit of min
3. Consumption: float, i.e. 19.2, represents the energy cumption of the bus task in the unit of kWh

