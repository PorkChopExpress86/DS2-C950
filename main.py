# Author: Blake Bowden
# Student ID: 001137627
import os

from Helper import *
from Truck import Truck


def clear_console():
    """Clear console for windows, mac and linux"""
    if os.name == "nt":
        _ = os.system("cls")
    else:
        _ = os.system("clear")


# Clear console
clear_console()

# User input on how many iterations for the genetic algorithm
while True:
    print(
        "Enter the number of iterations for the genetic algorithm to solve the route for"
        "each truck. Default is 1000 iterations, a larger number will take longer,"
        "but can get a shorter route.")
    num_iters = input("Number of Iterations (press Enter for 1000): ")
    if num_iters == "":
        print("Default settings, 1000 iterations...")
        num_iters = 1000
        break
    else:
        try:
            num_iters = int(num_iters)
            break
        except ValueError:
            print("Bad format for Iterations, please enter a number and try again...\n")

print("Loading truck...")


def load_truck_easy():
    """Manual loading of the truck packages
    Big(O): O(1)
    """
    truck1.packages = [7, 29, 19, 1, 13, 39, 20, 21, 4, 40, 14, 15, 16, 34, 30, 31]
    truck2.packages = [18, 36, 3, 8, 6, 32, 5, 37, 38, 25, 26]
    truck3.packages = [27, 35, 2, 33, 11, 28, 17, 12, 24, 23, 10, 22, 9]


print("Setting up data structures...")

# Fill hash table
hash_map = fill_hash_table("CSVFiles/packages.csv")

# Create distance matrix
distance_matrix = create_distance_matrix("CSVFiles/distance_table.csv")

# Create address index
address_index = create_address_dict("CSVFiles/addresses.csv")

# Set up parameters and create truck objects
speed = 18
truck1 = Truck(1, speed=speed, location="4001 S700 E",
               departure_time="08:00:00")  # early departure, more time sensitive packages
truck2 = Truck(2, speed=speed, location="4001 S700 E", departure_time="09:05:00")  # late arrival packages

truck3 = Truck(3, speed=speed, location="4001 S700 E", departure_time="10:20:00")  # EOD deliveries and left overs

# Load packages in trucks
load_truck_easy()

# Fill truck ids in packages
fill_package_truck_id(hash_map, truck1)
fill_package_truck_id(hash_map, truck2)
fill_package_truck_id(hash_map, truck3)

# Determine the route for each truck, if the route is not good enough increase the number of iterations
proceed = False
failures = 0
while not proceed:

    print("Determining truck 1 route...")
    # Truck 1
    truck1_package_indexes = convert_package_id_to_address_index(truck1.packages, address_index, hash_map)

    best1, score1 = genetic_algorithm(truck1_package_indexes, distance_matrix, address_index,
                                      hash_map, truck1, num_iter=num_iters, verbose=True)

    # Time to complete the route in hours
    truck1_total_time = score1 / truck1.speed

    # Update the finish time of the route
    truck1.finish_time = truck_finish_time(truck1, score1)

    print("[Determining truck 2 route...")

    # Truck 2
    truck2_package_indexes = convert_package_id_to_address_index(truck2.packages, address_index, hash_map)

    best2, score2 = genetic_algorithm(truck2_package_indexes, distance_matrix, address_index,
                                      hash_map, truck2, num_iter=num_iters, verbose=True)
    truck2_total_time = score2 / truck2.speed
    truck2.finish_time = truck_finish_time(truck2, score2)

    # Truck 3
    # Since truck 3 does not leave until 10:20 AM, the package address can be updated right before
    # the path is computed or until truck the first truck returns back to the hub, so which everyone is later will
    # be the departure time of truck3.
    print("Determining truck 3 route...")
    if convert_to_hours(truck1.finish_time) > convert_to_hours("10:20:00"):
        truck3.departure_time = truck1.finish_time

    # Update package address for package ID number 9
    hash_map.get_item(9).address = "410 S State St"

    truck3_package_indexes = convert_package_id_to_address_index(truck3.packages, address_index, hash_map)

    best3, score3 = genetic_algorithm(truck3_package_indexes, distance_matrix, address_index,
                                      hash_map, truck3, num_iter=num_iters, verbose=True)

    truck3_total_time = score3 / truck3.speed
    truck3.finish_time = truck_finish_time(truck3, score3)

    total_distance = score1 + score2 + score3
    if total_distance < 140:
        proceed = True
    else:
        failures += 1
        print("Route is too long, increasing iterations by 500 and running again")
        # If it keeps failing then the number of failures will scale the iterations by an exponent
        num_iters += 10 * pow(failures, failures)

print(f"Total trip distance is {total_distance:.2f} miles.")

distance_mat = distance_matrix

print("Updating package data...")
# Setting the delivery times of each package
truck1_route = delivery_times(truck1, best1, distance_mat, address_index, hash_map)
truck2_route = delivery_times(truck2, best2, distance_mat, address_index, hash_map)
truck3_route = delivery_times(truck3, best3, distance_mat, address_index, hash_map)

print("Done! Ready for user input")

# Forever loop to keep entering times and displaying a table of the data until the user enters quit or q
while True:
    some_time = input("\nEnter a time to check on all package statuses (hh:mm:ss), or enter Quit or Q to stop:")

    if some_time.lower() == "quit" or some_time.lower() == "q":
        print("Exiting program...")
        break
    elif some_time == "routes":
        # Print the routes out as a list of the address indexes
        print(f"Truck1:\n{best1}")
        print(f"Truck2:\n{best2}")
        print(f"Truck3:\n{best3}")
    else:
        try:
            h, m, s = some_time.split(":")
            if len(h) != 2 or len(m) != 2 or len(s) != 2:
                print(
                    "Bad time format, need two digits for Hour, Minute and Seconds, in this format hh:mm:ss"
                    "...\n")
            elif (int(h) < 0 or int(m) < 0 or int(s) < 0) or (int(h) >= 24 or int(m) >= 60 or int(s) >= 60):
                print("Please enter a time from 00:00:00 to 23:59:59")
            else:
                clear_console()
                display_all_trucks_distance(some_time, truck1, truck2, truck3)
                display_package_data_at_time(some_time, hash_map)

                x = input("Press any key to continue...")

        except ValueError:
            print("Bad time format, try again in this format hh:mm:ss...\n")
