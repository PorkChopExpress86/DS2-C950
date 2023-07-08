from HashTable import HashTable
from Package import Package
import csv


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
