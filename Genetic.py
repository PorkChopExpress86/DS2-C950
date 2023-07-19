import random

from HashTable import HashTable
from Package import Package
from Truck import Truck

random.seed(42)


# Create a population of some paths to start as the parents
def init_genetic_route(
        package_list,
        adjacency_mat,
        address_dict,
        num_routes,
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
    :param num_routes: a list of lists that contain pacakge ids in random orders
    :param hash_table: hash table class that contains packages with the package ids
    :param truck: truck object of a single truck
    :return: Population class

    Big(O): O(n) since it will loop over all packages in the truck
    """
    i = 0
    initial_routes = []
    while i < num_routes:
        rand_list = random.sample(package_list, len(package_list))
        if rand_list not in initial_routes:
            initial_routes.append(rand_list)
            i += 1

    return GeneticRoute(
        initial_routes,
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
    a, b = random.sample([x for x in range(len(chromosome))], 2)
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
        self.score = float('inf')
        self.best = None
        self.best_route_package_id = None
        self.adjacency_mat = adjacency_mat
        self.address_dict = address_dict
        self.hash_table = hash_table
        self.truck = truck

    def address_index_to_package_id(self, address_index: int) -> Package:
        """Convert the address index to an address and then convert the address to the package
        id by looping over the hash_table
        Big(O) = O(n^2)"""

        address: str = ""

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
        If the package is not delivered, then the total distance will have a 1000-mile penalty.
        :param chromosome: one of the routes from bag
        :return: distance of the route
        Big(O): O(n^3) There are 3 loops deep at the most
        """
        total_distance = 0
        # Copy the route, without reference in memory
        full_route = chromosome.copy()
        # Add the hub as the first element to be the starting location
        full_route.insert(0, 0)
        # Add the hub as the last element
        full_route.append(0)

        for i in range(len(full_route) - 1):
            total_distance += self.adjacency_mat[full_route[i]][full_route[i + 1]]

            # Loop over the route
            if full_route[i] != 0:
                # Get the index of the first stop
                address_index = int(full_route[i])

                address: str = ""
                # Get the address of the address index
                for key, value in self.address_dict.items():
                    if address_index == value:
                        address = key

                # Get the packages that will be delivered at that address, that are on the same truck
                packages = []
                for k in range(len(self.hash_table.data_map)):
                    if self.hash_table.data_map[k] is not None:
                        for j in range(len(self.hash_table.data_map[k])):
                            package = self.hash_table.data_map[k][j][1]
                            if (
                                    package.address == address
                                    and package.id in self.truck.packages
                            ):
                                packages.append(package)

                for package in packages:
                    deadline_str = package.deadline
                    if deadline_str != "EOD":

                        # Deliver time as hours
                        time_to_delivery = total_distance / self.truck.speed

                        # The total distance up to the address divided by the speed (18 mph) will determine
                        # if the deadline can be met. If the deadline cannot be met, then add 500 miles to the route.
                        deadline = _convert_to_hours(package.deadline)
                        departure = _convert_to_hours(self.truck.departure_time)

                        # Time to the deadline will be the deadline minus the departure in hours
                        time_to_deadline = deadline - departure

                        if time_to_deadline < time_to_delivery:
                            total_distance += 10000
                            break

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

        self.score = min(distances)
        self.best = self.bag[distances.index(self.score)]
        self.parents.append(self.best)

        # If there is only one element in distance
        if len(distances) == 1:
            distances = max(distances) - distances

        for i in range(len(distances)):
            # make an array of probability of distances
            distances[i] = distances[i] / sum(distances)
        return distances

    def select(self, k=4):
        """Select the parents of the next generation and append them to self.parent if it is above the random
        distribution
        Big(O): O(n)"""
        fit = self.evaluate()
        while len(self.parents) < k:
            idx = random.randint(0, len(fit) - 1)
            if fit[idx] > random.random():
                self.parents.append(self.bag[idx])

    def crossover(self, p_cross=0.1):
        """
        Randomly pick parts of the best route and randomly create different new routes based on the parent
        :param p_cross: probability to create a random part for another route
        :return: new routes for bag.
        Big(O) = O(n(n+n)) which will come out to O(n^2) for the loops inside a loop
        """
        children = []
        # Get the dimensions of self.parents
        count = len(self.parents)
        size = len(self.parents[0])

        # For all the routes in bag
        for _ in range(len(self.bag)):
            # By some change that p_cross is m
            if random.random() > p_cross:
                children.append(self.parents[random.randint(0, len(self.parents) - 1)])
            else:
                # Select a random part of a route and fill it in with the missing stops
                parent1, parent2 = random.sample(self.parents, 2)
                idx = random.sample(range(size), 2)
                start, end = min(idx), max(idx)
                child = [None] * size
                for i in range(start, end + 1, 1):
                    child[i] = parent1[i]

                # Fill in the extra missing stops with address indexes that are not in child
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
        This will call crossover to mix up the route and has a probably to swap some of the address indexes randomly
        :parm prob_cross: probability to create a random part for another route
        :parm prob_mut: probability to perform a swap on the route/chromosome
        :return: next_bag a list of the next children of the previous generation
        Big(O): O(n) looping over the list of children
        """
        bag2 = []
        children = self.crossover(prob_cross)
        for child in children:
            if random.random() < prob_mut:
                bag2.append(swap(child))
            else:
                bag2.append(child)
        return bag2
