# m2m_auth.py
import requests
from src.common.config.config import Auth

REQUESTED_SCOPES = ["full_access"]


class OAuth:
    def __init__(self):
        pass

    async def get_m2m_token(self, agent_name: str) -> str:  # TODO: REDIS
        """
        Request a machine-to-machine (M2M) OAuth2 access token for an agent.

        This function performs a client_credentials grant flow against Descope's
        authorization server. The scope used in the request is derived from the
        given agent name, which defines what resources or permissions the token
        should grant.

        Args:
            agent_scope (str): The logical name or identifier of the agent.
                This is mapped to one or more OAuth2 scopes that determine
                the level of access granted.

        Returns:
            str | None: A valid access token string if the request succeeds,
            otherwise None.
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": Auth.Descope.DESCOPE_CLIENT_ID,
            "client_secret": Auth.Descope.DESCOPE_CLIENT_SECRET,
            "scope": "full_access",
        }
        resp = requests.post(Auth.Descope.DESCOPE_TOKEN_URL, data=data, timeout=20)
        res = resp.json()
        token = res.get("access_token")
        return token
