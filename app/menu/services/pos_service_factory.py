# services/pos_service_factory.py
from .poster import PosterService


class POSServiceFactory:
    @staticmethod
    def get_service(venue):
        if venue.pos_system.name == "Poster":
            return PosterService(venue)
        else:
            raise NotImplementedError(f"POS system {venue.pos_system.name} is not supported")
