class Package:

    def __init__(
            self,
            package_id: int,
            address: str,
            city: str,
            state: str,
            zipcode: str,
            deadline: str,
            weight: str,
            note: str,
    ) -> None:
        """Package class that is initialized with the following parameters

        :param id (int) of the package number
        :param address (str) destination of the package
        :param city (str) city of the destination
        :param state (str) state of the destination
        :param zipcode (int) zipcode of the destination, entered as an int and stored as a string
        :param deadline (str) deadline of when the package must be delivered, in the format of "hh:mm:ss"
        :param weight (int) weight of the package in pounds
        :param note (str) text of the notes of the package
        :param status (str) of the package, at the hub, en route or delivered
        """
        self.id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.weight = int(weight)
        self.note = note
        self.departure_time = None
        self.delivery_time = None
        self.truck_id = None

    def __str__(self) -> str:
        return (
            f"\nPackage ID: {self.id}\n"
            f"\tStatus: {self.status}\n"
            f"\tDelivery Address: {self.address} {self.city}, UT, {self.zipcode}\n"
            f"\tDeadline: {self.deadline}\n"
            f"\tWeight: {self.weight}\n"
            f"\tSpecial Instructions: {self.note}\n"
            f"\tDeparture Time: {self.departure_time}\n"
            f"\tDelivery Time: {self.delivery_time}"
        )
