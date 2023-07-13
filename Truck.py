from Package import Package


def _convert_to_hours(some_time: str) -> float:
    h, m, s = some_time.split(":")
    hrs = float(h)
    hrs += float(m) / 60
    hrs += float(s) / (60 * 60)
    return hrs


class Truck:
    def __init__(self, truck_num: int, speed: int, location: str, departure_time: str = "08:00:00", ) -> None:
        self.id = truck_num
        self.speed = speed
        self.packages: list = []
        self.route: list = []
        self.total_distance: float = 0.0
        self.departure_time: str = departure_time
        self.finish_time: str = ""
        self.location: str = location
        self.max_package_capacity: int = 16
        self.package_addresses = []

    def add_package(self, package_id: int) -> bool:
        """Add package to truck
        Big(O): O(1)"""
        if self.is_full:
            return False
        self.packages.append(package_id)
        return True

    def print_packages(self) -> None:
        """Print the packages, used for debugging
        Big(O): O(n)"""
        for package in self.packages:
            print(package)

    @property
    def count_packages(self) -> int:
        return len(self.packages)

    @property
    def is_full(self) -> bool:
        if self.count_packages >= self.max_package_capacity:
            return True
        return False


# Pytest for the truck class
def test_truck():
    truck1 = Truck(1, 18)
    assert truck1.id == 1
    assert truck1.speed == 18
    package1 = Package(2, "1111", "Salt Lake City", "UT", "77777", "", "12", "")
    package2 = Package(2, "2222", "Salt Lake City", "UT", "76543", "", "2", "")
    truck1.add_package(package1.id)
    truck1.add_package(package2.id)
    # truck1.print_packages()

    truck1.departure_time = "08:00:00"
    test_time = "09:00:00"

    assert truck1.distance(test_time) == 18

    truck1.departure_time = "08:00:00"
    test_time = "14:00:00"

    assert truck1.distance(test_time) == 108

    truck1.finish_time = "12:00:00"
    assert truck1.distance(test_time) == 72
