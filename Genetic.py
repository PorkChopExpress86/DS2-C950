import numpy as np
from HashTable import HashTable
from Package import Package
from Truck import Truck

np.random.seed(42)


# Create a population of some paths to start as the parents
def init_genetic_route(
    package_list,
    adjacency_mat,
    address_dict,
    n_population,
    hash_table: HashTable,
    truck: Truck,
):
    """
    Initiate the parents of the generic algorithm. These routes will be the founders of the where the algorithm
    will improve.
    Big(O): O(n) where n = n_population

    :param package_list: list of the package id's to be delivered
    :param adjacency_mat: the distance matrix of the addresses
    :param address_dict: key value dict of address as keys and address index as value
    :param n_population: a subset of the population of route permutations
    :return: Population class

    Big(O): O(n) since it will loop over all packages in the truck
    """
    return GeneticRoute(
        np.asarray([np.random.permutation(package_list) for _ in range(n_population)]),
        adjacency_mat,
        address_dict,
        hash_table,
        truck,
    )


def swap(chromosome):
    """
    Swap parts of the route
    :param chromosome: a route from bag
    :return: a different route
    Big(O): O(1)
    """
    a, b = np.random.choice(len(chromosome), 2)
    chromosome[a], chromosome[b] = (
        chromosome[b],
        chromosome[a],
    )
    return chromosome


def _convert_to_hours(some_time: str) -> float:
    """Convert a string in the format of hh:mm:ss into hours as a float
    Big(O) = O(n) since split has to loop over the length of the string
    """
    h, m, s = some_time.split(":")
    hrs = float(h)
    hrs += float(m) / 60
    hrs += float(s) / (60 * 60)
    return hrs


class GeneticRoute:
    """This class will be used to determine a route for the trucks"""

    def __init__(
        self,
        bag,
        adjacency_mat: list,
        address_dict: dict,
        hash_table: HashTable,
        truck: Truck,
    ):
        self.bag = bag
        self.parents = []
        self.score = 0
        self.best = None
        self.best_route_package_id = None
        self.adjacency_mat = adjacency_mat
        self.address_dict = address_dict
        self.hash_table = hash_table
        self.truck = truck

    def address_index_to_package_id(self, address_index: int) -> Package:
        """Convert the address index to an address and then convert the address to the package
        id by looping over the hash_table
        Big(O) = O(n+n^2)"""

        # convert to address
        for key, value in self.address_dict.items():
            if value == address_index:
                address = key
                break

        # convert to package id
        for i in range(len(self.hash_table.data_map)):
            if self.hash_table.data_map[i] is not None:
                for j in range(len(self.hash_table.data_map[i])):
                    package = self.hash_table.data_map[i][j][1]
                    if package.address == address:
                        return package

    def fitness(self, chromosome) -> float:
        """
        Test the distance of a random route and check to see if the package will be delivered by the delivery time.
        If the package will not be delivered, then the total distance will have a 1000-mile penalty.
        :param chromosome: one of the routes from bag (np.array())
        :return: distance of the route
        Big(O): O(n) to loop the locations in a route, but there is a call to address_index_to_package_id that is O(n+n^2). The overall complexity to
        run this method is O(n(n+n+n)) or O(n^2)
        """
        total_distance = 0
        full_route = np.insert(chromosome, 0, 0)
        full_route = np.append(full_route, 0)
        for i in range(len(full_route) - 1):
            total_distance += self.adjacency_mat[full_route[i], full_route[i + 1]]

            # Loop over the route
            if full_route[i] != 0:
                # Get the index of the first stop
                address_index = int(full_route[i])

                # Get the address of the address index
                for key, value in self.address_dict.items():
                    if address_index == value:
                        address = key

                # Get the packages that will be delivered at that address, that are on the same truck
                packages = []
                for i in range(len(self.hash_table.data_map)):
                    if self.hash_table.data_map[i] is not None:
                        for j in range(len(self.hash_table.data_map[i])):
                            package = self.hash_table.data_map[i][j][1]
                            if (
                                package.address == address
                                and package.id in self.truck.packages
                            ):
                                packages.append(package)

                for package in packages:
                    # # Convert the address index -> package objects
                    # package = self.address_index_to_package_id(address_index)
                    deadline_str = package.deadline
                    if deadline_str != "EOD":
                        # Time to deliver the package in hours
                        time_to_delivery = total_distance / self.truck.speed

                        # The total distance up to the address divided by the speed (18 mph) will determine
                        # if the deadline can be met.If the deadline cannot be met then add 100 miles to the route.
                        deadline = _convert_to_hours(package.deadline)
                        departure = _convert_to_hours(self.truck.departure_time)

                        # Time to the deadline will be the deadline minus the departure in hours
                        time_to_deadline = deadline - departure

                        if time_to_deadline < time_to_delivery:
                            total_distance += 100

        return total_distance

    def evaluate(self):
        """
        Rank the route based on the fitness of all the routes in bag
        :return: the best route from bag
        Big(O): O(n) looping over all route in bag to pass to fitness, then O(1) for the rest of evaulate
        """
        distances = []
        for chromosome in self.bag:
            distance = self.fitness(chromosome=chromosome)
            distances.append(distance)
        distances = np.asarray(distances)
        self.score = np.min(distances)
        self.best = self.bag[distances.tolist().index(self.score)]
        self.parents.append(self.best)
        if False in (distances[0] == distances):
            distances = np.max(distances) - distances
        return distances / np.sum(distances)

    def select(self, k=4):
        fit = self.evaluate()
        while len(self.parents) < k:
            idx = np.random.randint(0, len(fit))
            if fit[idx] > np.random.rand():
                self.parents.append(self.bag[idx])
        self.parents = np.asarray(self.parents)

    def crossover(self, p_cross=0.1):
        """
        Randomly pick parts of the best route and randomly create different new routes based on the parent
        :param p_cross: probability to create a random part for another route
        :return: new routes for bag.
        Big(O) = O(n(n+n)) wich will come out to O(n^2) for the loops inside of a loop
        """
        children = []
        count, size = self.parents.shape
        for _ in range(len(self.bag)):
            if np.random.rand() > p_cross:
                children.append(list(self.parents[np.random.randint(count, size=1)[0]]))
            else:
                parent1, parent2 = self.parents[np.random.randint(count, size=2), :]
                idx = np.random.choice(range(size), size=2, replace=False)
                start, end = min(idx), max(idx)
                child = [None] * size
                for i in range(start, end + 1, 1):
                    child[i] = parent1[i]
                pointer = 0
                for i in range(size):
                    if child[i] is None:
                        while parent2[pointer] in child:
                            pointer += 1
                        child[i] = parent2[pointer]
                children.append(child)
        return children

    def mutate(self, prob_cross=0.1, prob_mut=0.1):
        """
        This will call crossover to mix up the route and has a probably change to swap some of the address
        :parm p_cross: probability to create a random part for another route
        :parm p_mut: probablity to perform a swap on the route/chromosome
        :return: next_bag a list of the next children of the previous generation
        Big(O): O(n) looping over the list of children
        """
        bag2 = []
        children = self.crossover(prob_cross)
        for child in children:
            if np.random.rand() < prob_mut:
                bag2.append(swap(child))
            else:
                bag2.append(child)
        return bag2

    def convert_address_index_to_package_id(self):
        """
        Convert the address indexes into package id's for best route.
        Use the common part of the address to link the two together.
        :return: list of package ids in the order of the best route
        Big(O): O(n^2) looping over the address_dict and the best list
        """
        address_route = []

        for key, value in self.address_dict.items():
            for item in self.best:
                if item == value:
                    address_route.append(key)
