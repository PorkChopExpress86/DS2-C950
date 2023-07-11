from Helper import *
from Genetic import *
from Truck import Truck

# from Package import Package
import os
from rich import print


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
        "Enter the number of [bold magenta]iterations[/bold magenta] for the genetic algorithm to solve the route for each truck. [bold green]Default is 1000 iterations[/bold green], [red]a larger number will take longer[/red], [green]but can get a shorter route.[/green]"
    )
    n_iters = input("Number of Iterations (press Enter for 1000): ")
    if n_iters == "":
        print("[blue]Default settings, 1000 iterations...")
        n_iters = 1000
        break
    else:
        try:
            n_iters = int(n_iters)
            break
        except:
            print("[bold red]Bad format for Iterations, try again...\n[/bold red]")

print("[blue]Loading truck...[/blue]")


def load_truck_easy():
    """Manual loading of the truck packages
    Big(O): O(1)
    """
    truck1.packages = [7, 29, 19, 1, 13, 39, 20, 21, 4, 40, 14, 15, 16, 34]
    truck2.packages = [18, 36, 3, 8, 30, 6, 31, 32, 5, 37, 38, 25, 26]
    truck3.packages = [27, 35, 2, 33, 11, 28, 17, 12, 24, 23, 10, 22, 9]


print("[blue]Setting up data structures...[/blue]")

# Fill hash table
hash_map = fill_hash_table("CSVFiles/packages.csv")

# Create distance matrix
distance_matrix = create_distance_matrix("CSVFiles/distance_table.csv")

# Create address index
address_index = create_address_dict("CSVFiles/addresses.csv")


# Set up parameters and create truck objects
# truck_packages = {}
speed = 18
truck1 = Truck(
    1, speed=speed, location="4001 S700 E", departure_time="08:00:00"
)  # early departure, more time sensitive packages
truck2 = Truck(
    2, speed=speed, location="4001 S700 E", departure_time="09:05:00"
)  # late arrival packages

truck3 = Truck(
    3, speed=speed, location="4001 S700 E", departure_time="10:20:00"
)  # EOD deliveries and left overs

# Load packages in trucks
load_truck_easy()

# Fill truck ids in packages
fill_package_truck_id(hash_map, truck1)
fill_package_truck_id(hash_map, truck2)
fill_package_truck_id(hash_map, truck3)

proceed = False
while proceed == False:
    print("[green]Determining truck 1 route...[/green]")
    # Truck 1
    truck1_package_indexes = convert_package_id_to_address_index(
        truck1.packages, address_index, hash_map
    )

    best1, score1 = genetic_algorithm(
        truck1_package_indexes,
        np.asarray(distance_matrix),
        address_index,
        hash_map,
        truck1,
        num_iter=n_iters,
        return_history=True,
        verbose=False,
    )

    # Time to complete the route in hours
    truck1_total_time = score1 / truck1.speed

    # Update the finish time of the route
    truck1.finish_time = truck_finish_time(truck1, score1)

    print("[green]Determining truck 2 route...[/green]")
    # Truck 2
    truck2_package_indexes = convert_package_id_to_address_index(
        truck2.packages, address_index, hash_map
    )

    best2, score2 = genetic_algorithm(
        truck2_package_indexes,
        np.asarray(distance_matrix),
        address_index,
        hash_map,
        truck2,
        num_iter=n_iters,
        return_history=True,
        verbose=False,
    )
    truck2_total_time = score2 / truck2.speed
    truck2.finish_time = truck_finish_time(truck2, score2)

    # Truck 3
    # Since truck 3 does not leave until 10:20 AM, the package address can be updated right before
    # the path is computed or until truck 1 returns back to the hub, so wich every one is later will
    # be the departure time of truck3.
    print("[green]Determining truck 3 route...[/green]")
    if convert_to_hours(truck1.finish_time) > convert_to_hours("10:20:00"):
        truck3.departure_time = truck1.finish_time

    # Update package address for package ID number 9
    hash_map.get_item(9).address = "410 S State St"

    truck3_package_indexes = convert_package_id_to_address_index(
        truck3.packages, address_index, hash_map
    )

    best3, score3 = genetic_algorithm(
        truck3_package_indexes,
        np.asarray(distance_matrix),
        address_index,
        hash_map,
        truck3,
        num_iter=n_iters,
        return_history=True,
        verbose=False,
    )

    truck3_total_time = score3 / truck3.speed
    truck3.finish_time = truck_finish_time(truck3, score3)

    total_distance = score1 + score2 + score2
    if total_distance < 140:
        proceed = True
    else:
        print(
            "[bold red]Route is too long, increasing iterations and running again[/bold red]"
        )
        n_iters += 500

print(f"[bold magenta]Total trip disance is {total_distance:.2f} miles.[/bold magenta]")

distance_mat = np.asarray(distance_matrix)

print("[blue]Updating package data...[/blue]")
truck1_route = delivery_times(truck1, best1, distance_mat, address_index, hash_map)
truck2_route = delivery_times(truck2, best2, distance_mat, address_index, hash_map)
truck3_route = delivery_times(truck3, best3, distance_mat, address_index, hash_map)

# # For auditing purposes, this will produce the overall distance and a 2d list of the route information in the following format:
# #[['address',[package_ids for address], distance traveled so far, delivery time]]
# print(f"Truck 1: {score1:.2f} miles\n{truck1_route}\n")
# print(f"Truck 2: {score2:.2f} miles\n{truck2_route}\n")
# print(f"Truck 3: {score3:.2f} miles\n{truck3_route}\n")

print("[blue]Done! Ready for user input[/blue]")

# Forever loop to keep entering times and displaying a table of the data until the user enters quit or q
while True:
    some_time = input(
        "\nEnter a time to check on all package statuses (hh:mm:ss), or enter Quit or Q to stop:"
    )

    if some_time.lower() == "quit" or some_time.lower() == "q":
        print("Exiting program...")
        break
    try:
        h, m, s = some_time.split(":")
        if len(h) != 2 or len(m) != 2 or len(s) != 2:
            print(
                "[bold red]Bad time format, need two digits for Hour, Minute and Seconds, in this format hh:mm:ss...\n[/bold red]"
            )
        else:
            clear_console
            display_package_data_at_time(some_time, hash_map)
            x = input("Press any key to continue...")
    except ValueError:
        print(
            "[bold red]Bad time format, try again in this format hh:mm:ss...\n[/bold red]"
        )
