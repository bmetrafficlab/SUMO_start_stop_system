import os
import startstop as Stp

"""
 Simulation settings: 
 For your own simulation, provide your own SUMO configuration.
 - sumoCfg: Path to the SUMO simulation's configuration file.
 - start_stop_ratio: Ratio of the start-stop vehicles in the simulation given in %.
 - ratio_based_simulation: If True, the vehicles are assigned to the start-stop vehicles group by the given ratio,
  otherwise, the vehicle class type "start-stop-vehicle" is used.
 - idle_time_in_sec: The amount of time the idle values are considered in seconds
 - idle_values: Dictionary of the idle emission values (CO2, CO, HC, NOx, PMx) based on the 
  HBEFA4/PC_petrol_Euro-4 model. Selected default parameters can be overwritten.
"""
# <-------------------- USER SETTINGS -------------------->
sumocfg = "examples/cfg_10_free.sumocfg"
ratio_based_simulation = True
start_stop_ratio = 80
idle_time_in_sec = 7
idle_values = None
# Example parameter selection:
#idle_values = {'CO2': 1.8, 'CO': 3.0126e-12}
# <-------------------- END OF USER SETTINGS -------------------->


def main():
    """
     Start-stop simulation functions. The user does not have to edit anything in the main function.
    """
    if start_stop_ratio > 100 or start_stop_ratio == 0:
        print("The start_stop_ratio must be larger than 0% and lower or equal to 100%!")
        return
    if sumocfg:
        if os.path.exists(sumocfg):
            print("Extracting SUMO configuration settings...")

            # Extract the step length size from the given SUMO configuration
            stepsize = float(Stp.extract_step_length(sumocfg))
            duration = float(Stp.extract_duration(sumocfg))

            # Start the simulation
            print("Starting SUMO simulation...")
            Stp.run_simulation(sumocfg, duration, stepsize, start_stop_ratio, ratio_based_simulation, idle_time_in_sec,
                               idle_values)
            return
        else:
            print("The given SUMO configuration file does not exist!")
            return
    else:
        print("Please provide a SUMO configuration file for the simulation.")
        return


if __name__ == "__main__":
    main()
