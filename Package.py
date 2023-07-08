def _convert_to_hours(some_time: str) -> float:
    h, m, s = some_time.split(":")
    hrs = float(h)
    hrs += float(m) / 60
    hrs += float(s) / (60 * 60)
    return hrs


class Package:
    """
    Package class that is initialized with the following parameters

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
        status: str = "At Hub",
    ) -> None:
        self.id = package_id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline
        self.weight = int(weight)
        self.status = status
        self.note = note
        self.departure_time = None
        self.delivery_time = None

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

    def set_status(self, some_time: str) -> None:
        some_time = _convert_to_hours(some_time)
        if self.delivery_time is not None:
            delivered_time = _convert_to_hours(self.delivery_time)
        if self.delivery_time is None and self.departure_time < some_time:
            self.status = "En Route"
        elif self.delivery_time <= some_time:
            self.status = "Delivered"
        else:
            self.status = "At Hub"
