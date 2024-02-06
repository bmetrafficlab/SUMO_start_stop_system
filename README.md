# SUMO_start_stop_system
Start-stop system based emission calculation for SUMO simulations.

This simulation tool provides a way to simulate vehicles with start-stop systems and analyze the effect of these vehicles on the emissions (CO2, CO, HC, NOx, PMx). 

The modeling approach is the following:
Restarting the engine will produce 7 seconds of idle emission levels, meaning the overall emission will be worse than the standard emission model. 

The simulation tool provides multiple ways to create start-stop vehicles:
-Ratio-based distribution of start-stop vehicles
-By defining a "start-stop-vehicle" vehicle type in SUMO

This way, any SUMO simulation can be executed with the start-stop vehicles.

The simulation creates a standard SUMO emission output (from the original, non-start-stop system simulation) and the same structured emission dump with the start-stop emissions.

It also provides information about the cumulated emissions of all types and shows the absolute differences of the cumulated emissions on a bar plot.

Usage:
Edit the user settings part of the main.py file.
Provide your sumocfg with all the necessary SUMO files (eg. vehicle routes). Decide if you want a ratio-based or a vehicle-type-based simulation. In the case of a vehicle-type simulation, make sure you have the vehicle type defined (see in the example "input_additional.add.xml"). This can also be applied to a vehicle flow (see the route_free.rou.xml).

The idle emission values are measured from SUMO's HBEFA4/PC_petrol_Euro-4 model. These parameters can be changed by overwriting the default parameters in the idle_values dictionary (an example is also given in the main.py file).

The simulation can be started by running the main.py script.

Example results:
Cumualted emissions for non start-stop case:
Sum of CO2: 79170873.11999595 mg
Sum of CO: 117.47000000000122 mg
Sum of HC: 0.0 mg
Sum of NOx: 31021.380000018416 mg
Sum of PMx: 812.7599999995496 mg
------------------------------
Cumualted emissions for start-stop case:
Sum of CO2: 79171616.54127455 mg
Sum of CO: 117.47088578857542 mg
Sum of HC: 5.816653829491e-06 mg
Sum of NOx: 31039.65995912361 mg
Sum of PMx: 812.7644484446845 mg
------------------------------
Absolute differences:
Difference of CO2: 743.4212785959244 mg
Difference of CO: 0.0008857885741946347 mg
Difference of HC: 5.816653829491e-06 mg
Difference of NOx: 18.279959105195303 mg
Difference of PMx: 0.00444844513492626 mg

![results](https://github.com/bmetrafficlab/SUMO_start_stop_system/assets/91676553/70f1904c-7237-4bd0-9017-b79f318dbb26)
