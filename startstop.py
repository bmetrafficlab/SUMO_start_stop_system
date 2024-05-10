import os
import xml.etree.ElementTree as ET
import traci
import matplotlib.pyplot as plt


def run_simulation(sumocfg, duration, steptime, start_stop_ratio, ratio_based_simulation, idle_time_in_sec,
                   idle_values=None):
    """
     A function to start the SUMO simulation with the given SUMO configuration using the extracted SUMO settings.
     SUMO is set to dump the emission data at the end of the simulation. The emission dump is then copied and
     overwritten by the start-stop emission data. This way, both the non start-stop data and start-stop data are saved.
    """
    # Create results folder if it does not exist
    if not os.path.exists("results"):
        os.makedirs("results")
        print("Results folder was created.")

    default_idle_values = {'CO2': 1.4,
                           'CO': 6.556e-11,
                           'HC': 4.569000000000001e-13,
                           'NOx': 0.611700000001176,
                           'PMx': 7.192094822220001e-05}

    if idle_values is None:
        idle_values = {'CO2': 1.4,
                       'CO': 6.556e-11,
                       'HC': 4.569000000000001e-13,
                       'NOx': 0.611700000001176,
                       'PMx': 7.192094822220001e-05}
    else:
        emission_types = ['CO2', 'CO', 'HC', 'NOx', 'PMx']

        for type in emission_types:
            if type not in idle_values:
                idle_values[type] = default_idle_values[type]

        print(idle_values)

    # Set the SUMO command to start SUMO with GUI and dump emissions to the results folder
    sumocmd = ["sumo-gui", "-c", sumocfg, "--start", "--emission-output", "results/emissions_default.xml"]
    # Start SUMO with the command
    traci.start(sumocmd)

    # Actual simulation time
    simulation_time = 0.00

    # Idle values
    idle_co2 = idle_values['CO2']
    idle_co = idle_values['CO']
    idle_hc = idle_values['HC']
    idle_nox = idle_values['NOx']
    idle_pmx = idle_values['PMx']

    # Idle emission for 7 seconds
    idle_co2_7s = idle_co2 * idle_time_in_sec
    idle_co_7s = idle_co * idle_time_in_sec
    idle_hc_7s = idle_hc * idle_time_in_sec
    idle_nox_7s = idle_nox * idle_time_in_sec
    idle_pmx_7s = idle_pmx * idle_time_in_sec

    # Data storages
    start_stop_data = {}
    regular_data = {}
    start_stop_vehicles = set()
    assigned_vehicles = set()
    total_vehicles_processed = 0
    vehicle_emission_data_per_step = {}

    stop_times = {}  # Dictionary to store stop times

    start_stop_threshold = start_stop_ratio / 100.0

    # Simulation steps
    for i in range(int(duration / steptime)):
        traci.simulationStep()
        current_vehicle_ids = set(traci.vehicle.getIDList())
        for vehicle_id in current_vehicle_ids:
            if vehicle_id not in assigned_vehicles:
                vehicle_type = traci.vehicle.getTypeID(vehicle_id)
                total_vehicles_processed += 1
                if ((len(start_stop_vehicles) / total_vehicles_processed) < start_stop_threshold and
                        ratio_based_simulation):
                    start_stop_vehicles.add(vehicle_id)
                elif vehicle_type == 'start-stop-vehicle':
                    start_stop_vehicles.add(vehicle_id)
                    traci.vehicle.setColor(vehicle_id, (255, 0, 0, 255))
                assigned_vehicles.add(vehicle_id)

            # Read current values
            current_speed = traci.vehicle.getSpeed(vehicle_id)
            current_co2 = traci.vehicle.getCO2Emission(vehicle_id)
            current_co = traci.vehicle.getCOEmission(vehicle_id)
            current_hc = traci.vehicle.getHCEmission(vehicle_id)
            current_nox = traci.vehicle.getNOxEmission(vehicle_id)
            current_pmx = traci.vehicle.getPMxEmission(vehicle_id)

            # Track stop times
            if current_speed == 0:
                stop_times[vehicle_id] = stop_times.get(vehicle_id, 0) + steptime

            # Start-stop functionality
            if vehicle_id in start_stop_vehicles:
                if current_speed == 0:
                    if vehicle_id not in start_stop_data:
                        start_stop_data[vehicle_id] = {'time': simulation_time, 'speed': current_speed,
                                                       'co2': current_co2, 'co': current_co, 'hc': current_hc,
                                                       'nox': current_nox, 'pmx': current_pmx}
                    else:
                        start_stop_data[vehicle_id]['time'] += steptime

                    # If the vehicle is not present in the emission data yet, it means it just stopped.
                    # It must be added with idle emissions.
                    if vehicle_id not in vehicle_emission_data_per_step:
                        vehicle_emission_data_per_step[vehicle_id] = {}
                        vehicle_emission_data_per_step[vehicle_id][simulation_time] = {'CO2': current_co2,
                                                                                       'CO': current_co,
                                                                                       'HC': current_hc,
                                                                                       'NOx': current_nox,
                                                                                       'PMx': current_pmx,
                                                                                       }
                    else:
                        # The vehicle was already in the emission data,
                        # meaning it is either still stopped or stopped again

                        # We check if the vehicle is stopped for more than 2 seconds
                        # If it is stopped for more than 2 seconds, the start-stop system stopped the engine
                        # we have to assign zero emissions until engine start
                        if start_stop_data[vehicle_id]['time'] > 2:
                            # Assuming engine is stopped, zero emission
                            vehicle_emission_data_per_step[vehicle_id][simulation_time] = {'CO2': 0.0,
                                                                                           'CO': 0.0,
                                                                                           'HC': 0.0,
                                                                                           'NOx': 0.0,
                                                                                           'PMx': 0.0
                                                                                           }
                        else:
                            # Engine still running in idle, enough to read current emission data and store them
                            vehicle_emission_data_per_step[vehicle_id][simulation_time] = {'CO2': current_co2,
                                                                                           'CO': current_co,
                                                                                           'HC': current_hc,
                                                                                           'NOx': current_nox,
                                                                                           'PMx': current_pmx,
                                                                                           }

                else:
                    # Vehicle is moving
                    if vehicle_id in start_stop_data:
                        # Check if it was stationary for more than 2 seconds
                        if start_stop_data[vehicle_id]['time'] >= 2:
                            adjusted_co2 = current_co2 + idle_co2_7s
                            start_stop_data[vehicle_id]['co2'] = adjusted_co2

                        if vehicle_id not in vehicle_emission_data_per_step:
                            if start_stop_data[vehicle_id]['time'] >= 2:
                                vehicle_emission_data_per_step[vehicle_id] = {}
                                vehicle_emission_data_per_step[vehicle_id][simulation_time] = {
                                    'CO2': current_co2 + idle_co2_7s,
                                    'CO': current_co + idle_co_7s,
                                    'HC': current_hc + idle_hc_7s,
                                    'NOx': current_nox + idle_nox_7s,
                                    'PMx': current_pmx + idle_pmx_7s}
                        else:
                            if start_stop_data[vehicle_id]['time'] >= 2:
                                vehicle_emission_data_per_step[vehicle_id][simulation_time] = {
                                    'CO2': current_co2 + idle_co2_7s,
                                    'CO': current_co + idle_co_7s,
                                    'HC': current_hc + idle_hc_7s,
                                    'NOx': current_nox + idle_nox_7s,
                                    'PMx': current_pmx + idle_pmx_7s}
                        start_stop_data[vehicle_id]['time'] = 0
                        start_stop_data[vehicle_id]['speed'] = current_speed
            else:
                # Regular vehicle data collection
                regular_data[vehicle_id] = {'time': simulation_time, 'speed': current_speed, 'co2': current_co2,
                                            'co': current_co, 'hc': current_hc,
                                            'nox': current_nox, 'pmx': current_pmx}

            simulation_time = i * steptime

    # Close TraCI
    traci.close()

    print("Simulation ended.")
    print("Starting emission data processing...")

    # Handle emission results
    if create_start_stop_emissions(vehicle_emission_data_per_step, stop_times):
        print("Start-stop emission data successfully written in results/emissions_start_stop.xml")
    else:
        print("Error in emission results handling!")
        return

    print("Calculating cumulative emissions...")
    calculate_cumulative_emissions()

    print("Program ended successfully.")
    return


def extract_step_length(sumocfg):
    """
     A function to extract the step-length setting from the SUMO configuration file given by the user.
     If the configuration does not contain the step-length, it defaults to 1.
    """
    tree = ET.parse(sumocfg)
    root = tree.getroot()
    step_length_value = 1

    for time_element in root.iter('time'):
        step_length = time_element.find('step-length')
        if step_length is not None:
            step_length_value = step_length.attrib.get('value')
            print("Step Length Value:", step_length_value)
        else:
            print("Step Length Value set to default:", step_length_value)
    return step_length_value


def extract_duration(sumocfg):
    """
     A function to extract the end time setting from the SUMO configuration file given by the user. If the configuration
     does not contain the end time, it defaults to 1000.
    """
    tree = ET.parse(sumocfg)
    root = tree.getroot()
    duration_value = 1000

    for time_element in root.iter('time'):
        duration = time_element.find('end')
        if duration is not None:
            duration_value = duration.attrib.get('value')
            print("End time:", duration_value)
        else:
            print("End time defaults to:", duration_value)
    return duration_value


def create_start_stop_emissions(start_stop_data, stop_times):
    """
    This function copies the original SUMO emissions XML file and replaces CO2 emission data for start-stop vehicles.
    :param start_stop_data: Contains data of the start-stop vehicles (dictionary)
    :param stop_times: Contains the stop time information for vehicles (dictionary)
    :return: Returns True when successfully done, or False on errors.
    """
    if start_stop_data and stop_times:
        original_emissions_file = "results/emissions_default.xml"
        start_stop_emissions_file = "results/emissions_start_stop.xml"

        # Copy the original emissions file
        if os.path.exists(original_emissions_file):
            if copy_file(original_emissions_file, start_stop_emissions_file):
                tree = ET.parse(start_stop_emissions_file)
                root = tree.getroot()

                for timestep in root.findall('timestep'):
                    # Extract time attribute
                    time = timestep.attrib['time']

                    # Iterate through vehicle elements
                    for vehicle in timestep.findall('vehicle'):
                        # Extract id attribute
                        vehicle_id = vehicle.attrib['id']
                        vehicle_id = str(vehicle_id)

                        # Find the vehicle id with the current timestep in the start-stop data
                        if start_stop_data is not None:
                            vehicle_start_stop = start_stop_data.get(vehicle_id, None)
                            if vehicle_start_stop is not None:
                                selected_vehicle_id = vehicle_start_stop.get(float(time), None)
                                if selected_vehicle_id is not None:
                                    vehicle.attrib['CO2'] = str(selected_vehicle_id['CO2'])
                                    vehicle.attrib['CO'] = str(selected_vehicle_id['CO'])
                                    vehicle.attrib['HC'] = str(selected_vehicle_id['HC'])
                                    vehicle.attrib['NOx'] = str(selected_vehicle_id['NOx'])
                                    vehicle.attrib['PMx'] = str(selected_vehicle_id['PMx'])

                                else:
                                    break
                # Write the modified XML back to file
                tree.write('results/emissions_start_stop.xml')
                return True
            else:
                return False
        else:
            print("Missing original emissions file! (results/emissions_default.xml)")
            return False
    else:
        print("Missing data in emission handling!")
        return False


def copy_file(original_file, new_file):
    """
    This function is to copy the original emission file before modifying it with the stop-start data.
    :param original_file: The original file to copy.
    :param new_file: The new file's path and extension.
    :return: True on success and False on failure.
    """
    try:
        with open(original_file, 'rb') as f_original:
            with open(new_file, 'wb') as f_new:
                # Read from the original file and write to the new file
                f_new.write(f_original.read())
        print(f"File '{original_file}' copied to '{new_file}' successfully.")
        return True
    except FileNotFoundError:
        print("One of the files doesn't exist.")
        return False


def calculate_cumulative_emissions():
    # Parse the XML file
    tree = ET.parse('results/emissions_default.xml')
    root = tree.getroot()

    # Initialize sums for each emission type
    sum_CO2 = 0
    sum_CO = 0
    sum_HC = 0
    sum_NOx = 0
    sum_PMx = 0

    # Iterate through each timestep
    for timestep in root.findall('timestep'):
        # Iterate through each vehicle within the timestep
        for vehicle in timestep.findall('vehicle'):
            # Extract and sum the values for each emission type
            sum_CO2 += float(vehicle.get('CO2'))
            sum_CO += float(vehicle.get('CO'))
            sum_HC += float(vehicle.get('HC'))
            sum_NOx += float(vehicle.get('NOx'))
            sum_PMx += float(vehicle.get('PMx'))

    # Print the sum of each emission type
    print("------------------------------")
    print("Cumulated emissions for non start-stop case:")
    print("Sum of CO2:", sum_CO2, "mg")
    print("Sum of CO:", sum_CO, "mg")
    print("Sum of HC:", sum_HC, "mg")
    print("Sum of NOx:", sum_NOx, "mg")
    print("Sum of PMx:", sum_PMx, "mg")

    # Parse the XML file
    tree = ET.parse('results/emissions_start_stop.xml')
    root = tree.getroot()

    # Initialize sums for each emission type
    sum_CO2_start_stop = 0
    sum_CO_start_stop = 0
    sum_HC_start_stop = 0
    sum_NOx_start_stop = 0
    sum_PMx_start_stop = 0

    # Iterate through each timestep
    for timestep in root.findall('timestep'):
        # Iterate through each vehicle within the timestep
        for vehicle in timestep.findall('vehicle'):
            # Extract and sum the values for each emission type
            sum_CO2_start_stop += float(vehicle.get('CO2'))
            sum_CO_start_stop += float(vehicle.get('CO'))
            sum_HC_start_stop += float(vehicle.get('HC'))
            sum_NOx_start_stop += float(vehicle.get('NOx'))
            sum_PMx_start_stop += float(vehicle.get('PMx'))

    # Print the sum of each emission type
    print("------------------------------")
    print("Cumulated emissions for start-stop case:")
    print("Sum of CO2:", sum_CO2_start_stop, "mg")
    print("Sum of CO:", sum_CO_start_stop, "mg")
    print("Sum of HC:", sum_HC_start_stop, "mg")
    print("Sum of NOx:", sum_NOx_start_stop, "mg")
    print("Sum of PMx:", sum_PMx_start_stop, "mg")
    print("------------------------------")
    print("Absolute differences:")
    print("Difference of CO2:", abs(sum_CO2_start_stop - sum_CO2), "mg")
    print("Difference of CO:", abs(sum_CO_start_stop - sum_CO), "mg")
    print("Difference of HC:", abs(sum_HC_start_stop - sum_HC), "mg")
    print("Difference of NOx:", abs(sum_NOx_start_stop - sum_NOx), "mg")
    print("Difference of PMx:", abs(sum_PMx_start_stop - sum_PMx), "mg")

    categories = ['CO2', 'CO', 'HC', 'NOx', 'PMx']
    values = [abs(sum_CO2_start_stop - sum_CO2), abs(sum_CO_start_stop - sum_CO), abs(sum_HC_start_stop - sum_HC),
              abs(sum_NOx_start_stop - sum_NOx), abs(sum_PMx_start_stop - sum_PMx)]
    # Create bar graph
    plt.bar(categories, values, color='skyblue')

    # Adding title and labels
    plt.title('Absolute difference of total emissions')
    plt.xlabel('Emission type')
    plt.ylabel('Absolute difference [mg]')

    # Show the plot
    plt.show()
    return
