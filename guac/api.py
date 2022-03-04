import logging
import random
import requests
import string
import urllib.parse

from . import models

default_username = "guacadmin"


LOG = logging.getLogger(__name__)


def random_string(stringlen: int):
    return "".join(
        random.choice(string.ascii_letters + string.digits + string.punctuation)
        for i in range(stringlen)
    )


class Endpoints:
    def __init__(self, datasource):
        self.datasource = datasource

    @property
    def base(self):
        return f"/api/session/data/{self.datasource}"

    @property
    def user(self):
        return f"{self.base}/users"

    @property
    def connection(self):
        return f"{self.base}/connections"


class Guacamole(requests.Session):
    token: str

    def __init__(
        self,
        baseurl,
        token=None,
        username=None,
        password=None,
        datasource="postgresql",
    ):
        super().__init__()

        self.baseurl = baseurl
        self.endpoints = Endpoints(datasource)
        self.username = username if username else default_username
        self.password = password
        self.token = token
        self.headers["content-type"] = "application/json"

        if self.token is None:
            self.get_token()

        self.headers["guacamole-token"] = self.token

    def get_token(self):
        auth = {
            "username": self.username,
            "password": self.password,
        }

        res = self.post(
            "/api/tokens",
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=auth,
        )
        res.raise_for_status()

        self._token_response = res.json()
        self.token = self._token_response["authToken"]

    def request(self, method, url, *args, **kwargs):
        if not url.startswith("http"):
            url = urllib.parse.urljoin(self.baseurl, url)

        LOG.debug("url = %s", url)
        return super().request(method, url, *args, **kwargs)

    def connection_list(self):
        res = self.get(self.endpoints.connection)
        res.raise_for_status()
        return res.json()

    def connection_exists(self, conname):
        return any(
            connection["name"] == conname
            for connection in self.connection_list().values()
        )

    def connection_delete(self, conname):
        try:
            cid, config = self.connection_find(conname)
            res = self.delete(f"{self.endpoints.connection}/{cid}")
            res.raise_for_status()
        except KeyError:
            pass

    def connection_add(self, connection):
        res = self.post(self.endpoints.connection, json=connection)
        return res.status_code == 200, res.json()

    def connection_find(self, conname):
        for k, v in self.connection_list().items():
            if v["name"] == conname:
                return k, v
        raise KeyError(conname)

    def user_grant_connection(self, username, conname):
        cid, _ = self.connection_find(conname)
        patch = [
            {"op": "add", "path": f"/connectionPermissions/{cid}", "value": "READ"}
        ]
        res = self.patch(f"{self.endpoints.user}/{username}/permissions", json=patch)
        res.raise_for_status()

    def user_exists(self, username):
        res = self.get(f"{self.endpoints.user}/{username}")
        return res.status_code == 200

    def user_delete(self, username):
        res = self.delete(f"{self.endpoints.user}/{username}")
        try:
            res.raise_for_status()
        except requests.HTTPError as err:
            if err.response.status_code != 404:
                raise

    def user_add(self, username, password=None, fullname=None):
        # If caller does not provide a password, set it to a long
        # random string. Creating a user with no password will allow
        # password-free login.
        if password is None:
            password = random_string(60)

        u = models.User(username=username, password=password)
        if fullname:
            u.attributes.guac_full_name = fullname

        res = self.post(self.endpoints.user, json=u.dict(by_alias=True))
        res.raise_for_status()

        return res.status_code == 200, res.json()
