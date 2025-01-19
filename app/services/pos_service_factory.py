from .poster import PosterService


class POSServiceFactory:
    @staticmethod
    def get_service(pos_system_name, api_token):
        if pos_system_name == "poster":
            return PosterService(api_token)
        else:
            raise NotImplementedError(f"POS system {pos_system_name} is not supported")
