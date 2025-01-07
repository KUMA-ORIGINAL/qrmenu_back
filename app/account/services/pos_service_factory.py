from .poster import PosterService


class POSServiceFactory:
    @staticmethod
    def get_service(pos_system, api_token):
        if pos_system.name == "Poster":
            return PosterService(api_token)
        else:
            raise NotImplementedError(f"POS system {pos_system.name} is not supported")
