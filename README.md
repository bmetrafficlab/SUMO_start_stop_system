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
