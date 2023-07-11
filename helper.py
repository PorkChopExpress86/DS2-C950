from HashTable import HashTable
from Package import Package
from Truck import Truck
import csv
import numpy as np
from Genetic import *
from prettytable import PrettyTable


def fill_hash_table(packages_csv: str) -> HashTable:
    """
    Fill hashtable with the package objects, using the package's id as the key.

    :param packages_csv: string path to the packages.csv
    :return: HashTable of the package objects
    Big(O): O(n) looping over the csv file line by line to fill the hashTable
    """
    hash_table = HashTable()
    with open(packages_csv) as file:
        csv_file = csv.reader(file)
        for index, line in enumerate(csv_file):
            package = Package(
                index + 1, line[0], line[1], line[2], line[3], line[4], line[5], line[6]
            )
            hash_table.insert(package.id, package)
    return hash_table


def create_distance_matrix(distance_table_path: str) -> list:
    """
    Create 2D list of distances without header or addresses, and convert all the strings to float or None.

    :param distance_table_path:
    :return: list of a list containing the distance matrix
    Big(O): O(n) since there is a for loop going over every line in the csv
    """
    distance_list = []
    with open(distance_table_path) as csv_file:
        for index, line in enumerate(csv_file):
            row = line.replace("\n", "").split(",")
            row = [float(i) if i != "None" else None for i in row]
            distance_list.append(row)
    return distance_list


def convert_to_hours(some_time: str) -> float:
    h, m, s = some_time.split(":")
    hrs = float(h)
    hrs += float(m) / 60
    hrs += float(s) / (60 * 60)
    return hrs


def create_address_dict(addresses_csv_path):
    """
    Create a dictionary of the address and their index. The address is the key and the index are the value.
    This will be used in the package look up and for the distance table lookup, the higher value will go to
    the row and the lower number will be the column.

    :param addresses_csv_path: string path of the csv containing all the address
    :return: dictionary with address as the key and int as the value.
    Big(O): O(n) looping over each line in the csv
    """
    address_dict = {}
    with open(addresses_csv_path) as csv_file:
        for index, line in enumerate(csv_file):
            address_dict[line.replace("\n", "").split(",")[1]] = index
    return address_dict


def create_address_list(addresses_csv_path):
    address_list = []
    with open(addresses_csv_path) as csv_file:
        for index, line in enumerate(csv_file):
            address_list.append(line.replace("\n", "").split(",")[1])
    return address_list


def convert_package_id_to_address_index(
    truck_packages: list, addresses_index: dict, hash_map: HashTable
) -> list:
    """Convert the trucks package list of id's into the indexes of the address list"""
    truck_address_list = []
    for package_id in truck_packages:
        package_address = hash_map.get_item(package_id).address
        address_index = addresses_index[package_address]
        truck_address_list.append(address_index)
    return list(set(truck_address_list))


def create_address_dict_int_to_address(addresses_csv_path):
    """
    Create a dictionary of the address and their index. The address is the key and the index are the value.
    This will be used in the package look up and for the distance table lookup, the higher value will go to
    the row and the lower number will be the column.

    :param addresses_csv_path: string path of the csv containing all the address
    :return: dictionary with address as the key and int as the value.
    Big(O): O(n) looping over each line in the csv
    """
    address_mat = {}
    with open(addresses_csv_path) as csv_file:
        for index, line in enumerate(csv_file):
            address_mat[index] = line.replace("\n", "").split(",")[1]
    return address_mat


def genetic_algorithm(
    location_indexes,
    adjacency_mat,
    address_index,
    hash_map,
    truck,
    num_population=25,
    num_iter=1000,
    selectivity=0.15,
    prob_cross=0.5,
    prob_mut=0.1,
    print_interval=100,
    return_history=False,
    verbose=False,
):
    """Method to call the genetic algorith to find an optimal route
    :param location_indexes:
    :param adjacency_mat:
    :param address_index:
    :param hash_map:
    :param truck:
    :param n_population:
    :param n_iter:
    :param selectivity:
    :param p_cross:
    :param p_mut:
    :param print_interval:
    :param return_history:
    :param verbose:
    """
    location_indexes = np.array(location_indexes)

    route = init_genetic_route(
        location_indexes, adjacency_mat, address_index, num_population, hash_map, truck
    )

    best = route.best
    score = float("inf")
    history = []

    for i in range(num_iter):
        route.select(num_population * selectivity)
        history.append(route.score)
        if verbose:
            print(f"Generation {i}: {route.score}")
        # elif i % print_interval == 0:
        #     print(f"Generation {i}: {pop.score}")
        if route.score < score:
            best = route.best
            best = np.insert(best, 0, 0)
            best = np.append(best, 0)
            score = route.score
        children = route.mutate(prob_cross, prob_mut)
        route = GeneticRoute(children, route.adjacency_mat, address_index, hash_map, truck)
    if return_history:
        return best, score
    return best


def truck_finish_time(truck: Truck, score: float) -> str:
    """Determine the finish time of the truck for the route distance
    :param truck: truck object
    :param score: the distance of the route in miles
    :return: string of the time the truck returns to the hub
    Big(O): O(1)"""
    departure_hours = convert_to_hours(truck.departure_time)
    finish_hours = departure_hours + score / truck.speed
    return hours_to_string(finish_hours)


def hours_to_string(some_time: float) -> str:
    """Convert hours as a float to a time as in hh:mm:ss as a string
    :param some_time: hours as a float
    :return: string of the time in the format hh:mm:ss in 24 hour time
    Big(O): O(1)"""
    hours = int(some_time - (some_time % 1))
    minutes = (some_time % 1) * 60
    seconds = (minutes % 1) * 60
    minutes = int(round(minutes, 0))
    seconds = int(round(seconds, 0))
    if seconds == 60:
        minutes += 1
        seconds = 0
    if minutes == 60:
        hours += 1
        minutes = 0
    if 0 <= hours < 10:
        hours_str = "0" + str(int(hours))
    else:
        hours_str = str(hours)
    if 0 <= minutes < 10:
        minutes_str = "0" + str(minutes)
    else:
        minutes_str = str(minutes)

    if 0 <= seconds < 10:
        seconds_str = "0" + str(seconds)
    else:
        seconds_str = str(seconds)

    return f"{hours_str}:{minutes_str}:{seconds_str}"


def delivery_times(
    truck: Truck,
    route: list,
    distance_mat: list,
    address_index: dict,
    hash_table: HashTable,
) -> list:
    """Enter the times the packages on the truck will be delivered to the address
    given the route by the genetic algorithm. The route is a list of the address indexes,
    not the package ids

    :param truck: Truck class of the truck that contains the packages
    :param route: List of the address indexes in the order of the route. Each index may have many packages
    :param distance_mat: the 2d list of the distance matrix
    :return: None
    """
    total_distance = 0
    deliver_route = []
    # get a list of the distances from one stop to the next
    for stop in range(len(route) - 1):
        total_distance += distance_mat[route[stop], route[stop + 1]]

        if route[stop + 1] != 0:
            # This list will be used to check the route
            # [[address, [packages], total distance]]
            stop_route = []
            # Get the packages that may be delivered to the address
            # convert to address
            for key, value in address_index.items():
                if value == route[stop + 1]:
                    address = key
                    stop_route.append(address)
                    break

            # convert to package id
            packages = []
            for i in range(len(hash_table.data_map)):
                if hash_table.data_map[i] is not None:
                    for j in range(len(hash_table.data_map[i])):
                        package = hash_table.data_map[i][j][1]
                        if package.address == address and package.id in truck.packages:
                            packages.append(package)
            stop_route_package = []
            delivery_time = 0
            for p in packages:
                stop_route_package.append(p.id)
                departure_time = convert_to_hours(truck.departure_time)
                total_time = departure_time + (total_distance / truck.speed)
                p.delivery_time = hours_to_string(total_time)
                p.departure_time = truck.departure_time
                delivery_time = p.delivery_time
            stop_route.append(stop_route_package)
            stop_route.append(total_distance)
            stop_route.append(delivery_time)
            deliver_route.append(stop_route)

    return deliver_route


def display_package_data_at_time(some_time: str, hash_table: HashTable):
    """Loop over all of the packages in the hashtable to check the delivery
    times against some_time. Since we will already know what time the package
    will be delivered, check to see if the delivery time of the package is less
    than or equal to some_time.
    :param some_time: string format that the user will enter as "hh:mm:ss"
    :return: None, it will print the status of all of the packages.
    """
    some_time_float = convert_to_hours(some_time)

    # Check for package_id number 9, if some_time is less than 10:20 then
    # it is the original address
    if convert_to_hours("10:20:00") > some_time_float:
        hash_table.get_item(9).address = "300 State St"
    else:
        hash_table.get_item(9).address = "410 S State St"

    # Loop over all of the packages in the hashtable to check
    # Since we will already know what time the package will be delivered,
    # check to see if the delivery time of the package is less than or
    # equal to some_time
    table_list = [
        ["Package ID", "Delivery Address", "Truck Number", "Status", "Time of Delivery"]
    ]
    package_id_list = [id for id in range(1, hash_table.get_number_of_packages() + 1)]
    package_id_list.sort()

    for package_id in package_id_list:
        package = hash_table.get_item(package_id)
        temp = []
        temp.append(package.id)
        temp.append(package.address)
        temp.append(package.truck_id)

        package_delivery = convert_to_hours(package.delivery_time)
        if package_delivery <= some_time_float:
            temp.append("Delivered")
            temp.append(package.delivery_time)
        elif convert_to_hours(package.departure_time) <= some_time_float:
            temp.append("In Route")
            temp.append(f"ETA: {package.delivery_time}")
        else:
            temp.append("At Hub")
            temp.append(f"ETA: {package.delivery_time}")
        table_list.append(temp)

    print(f"Package status table at {some_time}:")
    table = PrettyTable(table_list[0])
    table.add_rows(table_list[1:])
    print(table)


def fill_package_truck_id(hash_table: HashTable, truck: Truck) -> None:
    """Add the truck_id to the packge for the display table by looping over truck.packages
    :param hash_table: hash table of the packages for easy look up
    :param truck: the truck object
    :return: None
    """

    for package_id in truck.packages:
        package = hash_table.get_item(package_id)
        package.truck_id = truck.id
