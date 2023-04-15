import rest_framework.authentication
from .models import WebpageToken, APIToken


class WebpageTokenAuth(rest_framework.authentication.TokenAuthentication):
    """
    Authentication check to ensure request has the header:

    .. code-block:: yaml

        Authorization: Token <WebpageToken.key>
    """
    model = WebpageToken


class APITokenAuth(rest_framework.authentication.TokenAuthentication):
    """
    Authentication check to ensure request has the header:

    .. code-block:: yaml

        Authorization: Token <APIToken.key>
    """
    model = APIToken
