from HashTable import HashTable
from Package import Package
from Truck import Truck
import csv
import numpy as np
from Genetic import *


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
    address_dict = {}
    with open(addresses_csv_path) as csv_file:
        for index, line in enumerate(csv_file):
            address_dict[index] = line.replace("\n", "").split(",")[1]
    return address_dict


def genetic_algorithm(
    location_indexes,
    adjacency_mat,
    address_index,
    hash_map,
    truck,
    n_population=25,
    n_iter=1000,
    selectivity=0.15,
    p_cross=0.5,
    p_mut=0.1,
    print_interval=100,
    return_history=False,
    verbose=False,
):
    location_indexes = np.array(location_indexes)

    pop = init_population(
        location_indexes, adjacency_mat, address_index, n_population, hash_map, truck
    )

    best = pop.best
    score = float("inf")
    history = []

    for i in range(n_iter):
        pop.select(n_population * selectivity)
        history.append(pop.score)
        if verbose:
            print(f"Generation {i}: {pop.score}")
        # elif i % print_interval == 0:
        #     print(f"Generation {i}: {pop.score}")
        if pop.score < score:
            best = pop.best
            best = np.insert(best, 0, 0)
            best = np.append(best, 0)
            score = pop.score
        children = pop.mutate(p_cross, p_mut)
        pop = Population(children, pop.adjacency_mat, address_index, hash_map, truck)
    if return_history:
        return best, score
    return best


def convert_address_id_to_address(hash_map: HashTable, best: list, address_list: list):
    delivery_route_address = []
    delivery_route_package_id = []

    # Get the addresses in the route
    for address_id in best:
        for address_index, address in enumerate(address_list):
            if address_id == address_index:
                delivery_route_address.append(address)
    return delivery_route_address  # , delivery_route_package_id


def truck_finish_time(truck: Truck, score: float):
    departure_time = convert_to_hours(truck.departure_time)
    total_time = departure_time + score / truck.speed
    return hours_to_string(total_time)


def hours_to_string(some_time: float) -> str:
    hours = int(some_time - (some_time % 1))
    minutes = (some_time % 1) * 60
    seconds = (minutes % 1) * 60
    minutes = int(minutes)
    seconds = int(round(seconds, 0))
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


def package_delivery_time(departure_time: str, elasped_time: str) -> str:
    depart_hours = convert_to_hours(departure_time)
    delivery_hour = depart_hours + convert_to_hours(elasped_time)


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
    for stop in range(len(route)-1):
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
                total_time = convert_to_hours(truck.departure_time) + (
                    total_distance / truck.speed
                )
                p.delivery_time = hours_to_string(total_time)
                delivery_time = p.delivery_time
            stop_route.append(stop_route_package)
            stop_route.append(total_distance)
            stop_route.append(delivery_time)
            deliver_route.append(stop_route)

    return deliver_route
