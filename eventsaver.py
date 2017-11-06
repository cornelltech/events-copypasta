import abc

class EventSaver():
    __metaclass__ = abc.ABCMeta

    def __init__(self, url):
        self.url = url

    @abc.abstractmethod
    def get_title(self):
        """The event's title."""

    @abc.abstractmethod
    def get_start_time(self):
        """The event's starting time."""

    @abc.abstractmethod
    def get_end_time(self):
        """The event's end time."""

    @abc.abstractmethod
    def get_description(self):
        """The event's description."""

    @abc.abstractmethod
    def get_location(self):
        """The event's location."""

    def get_url(self):
        return self.url

# start_time=start_time,
# end_time=end_time,
# description=description,
# external_url=external_url,
# location_id=location_id,
