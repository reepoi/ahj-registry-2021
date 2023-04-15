from rest_framework.throttling import UserRateThrottle


def user_has_active_api_token(user):
    """
    Determines if a user has API token and whether it is active.
    """
    api_token = user.get_API_token()
    return api_token is not None and api_token.is_active


def user_is_sunspec_alliance_member(user):
    """
    Determines if a user is or is part of a SunSpec Alliance member organization.
    """
    return user.MemberID is not None


class SunSpecAllianceMemberRateThrottle(UserRateThrottle):
    # Define a custom scope name to be referenced by DRF in settings.py
    scope = 'sunspecalliancemember'

    def allow_request(self, request, view):
        """
        Override this method to implement more elaborate throttling schemes.
        In addition, overriding parse_rate may be useful; such as for adding a monthly rate.
        Update this doc-string if such a scheme has been implemented.
        """
        return super().allow_request(request, view)
