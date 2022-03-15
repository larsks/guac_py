import logging
import requests
import urllib.parse

import guac.models
import guac.utils

default_username = "guacadmin"


LOG = logging.getLogger(__name__)


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

    @property
    def group(self):
        return f"{self.base}/userGroups"


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
        return [guac.models.Connection(id=k, **v) for k, v in res.json().items()]

    def connection_exists(self, cname):
        return any(conn.name == cname for conn in self.connection_list())

    def connection_delete(self, cname):
        try:
            conn = self.connection_find(cname)
            res = self.delete(f"{self.endpoints.connection}/{conn.id}")
            res.raise_for_status()
        except KeyError:
            pass

    def connection_add(self, connection):
        res = self.post(self.endpoints.connection, json=connection)
        return guac.models.Connection(**res.json())

    def connection_find(self, cname):
        LOG.debug("looking for connection name=%s", cname)
        for conn in self.connection_list():
            if conn.name == cname:
                LOG.debug("found connection name=%s, id=%s", conn.name, conn.id)
                return conn
        raise KeyError(cname)

    def user_list(self):
        res = self.get(self.endpoints.user)
        res.raise_for_status()
        return res.json().values()

    def user_grant_connection(self, username, cname):
        conn = self.connection_find(cname)
        patch = [
            {"op": "add", "path": f"/connectionPermissions/{conn.id}", "value": "READ"}
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
            password = guac.utils.random_string(60)

        u = guac.models.User(username=username, password=password)
        if fullname:
            u.attributes.guac_full_name = fullname

        res = self.post(self.endpoints.user, json=u.dict(by_alias=True))
        res.raise_for_status()

        return guac.models.User(**res.json())

    def group_get(self, groupname):
        res = self.get(f"{self.endpoints.group}/{groupname}")
        res.raise_for_status()
        return guac.models.Group(**res.json())

    def group_get_permissions(self, groupname):
        res = self.get(f"{self.endpoints.group}/{groupname}/permissions")
        res.raise_for_status()
        return guac.models.GroupPermissions(**res.json())

    def group_set_connection_permissions(
        self, groupname, connection, add=None, remove=None
    ):
        if not add and not remove:
            return

        changes = []

        for perm in add:
            changes.append(
                {
                    "op": "add",
                    "path": f"/connectionPermissions/{connection}",
                    "value": perm.upper(),
                },
            )
        for perm in remove:
            changes.append(
                {
                    "op": "remove",
                    "path": f"/connectionPermissions/{connection}",
                    "value": perm.upper(),
                },
            )

        LOG.debug(
            "setting connection permissions for group %s connection %s to: %s",
            groupname,
            connection,
            changes,
        )
        res = self.patch(
            f"{self.endpoints.group}/{groupname}/permissions", json=changes
        )
        res.raise_for_status()

    def group_set_system_permissions(self, groupname, add=None, remove=None):
        if not add and not remove:
            return

        changes = []

        for perm in add:
            changes.append(
                {"op": "add", "path": "/systemPermissions", "value": perm.upper()},
            )
        for perm in remove:
            changes.append(
                {"op": "remove", "path": "/systemPermissions", "value": perm.upper()},
            )

        LOG.debug("setting permissions for group %s to: %s", groupname, changes)
        res = self.patch(
            f"{self.endpoints.group}/{groupname}/permissions", json=changes
        )
        res.raise_for_status()

    def user_get(self, username):
        res = self.get(f"{self.endpoints.user}/{username}")
        res.raise_for_status()
        return guac.models.User(**res.json())

    def user_get_permissions(self, username):
        res = self.get(f"{self.endpoints.user}/{username}/permissions")
        res.raise_for_status()
        return guac.models.UserPermissions(**res.json())

    def group_add(self, groupname):
        g = guac.models.Group(groupname=groupname)
        res = self.post(self.endpoints.group, json=g.dict(by_alias=True))
        res.raise_for_status()
        return guac.models.Group(**res.json())

    def group_list(self):
        res = self.get(self.endpoints.group)
        res.raise_for_status()
        return [guac.models.Group(**grp) for grp in res.json().values()]

    def group_delete(self, groupname):
        res = self.delete(f"{self.endpoints.group}/{groupname}")
        try:
            res.raise_for_status()
        except requests.HTTPError as err:
            if err.response.status_code != 404:
                raise

    def group_add_connection(self, groupname, cname):
        conn = self.connection_find(cname)
        changes = [
            {
                "op": "add",
                "path": f"/connectionPermissions/{conn.id}",
                "value": "READ",
            }
        ]
        res = self.patch(
            f"{self.endpoints.group}/{groupname}/permissions", json=changes
        )
        res.raise_for_status()

    def group_remove_connection(self, groupname, cname):
        conn = self.connection_find(cname)
        changes = [
            {
                "op": "remove",
                "path": f"/connectionPermissions/{conn.id}",
                "value": "READ",
            }
        ]
        res = self.patch(
            f"{self.endpoints.group}/{groupname}/permissions", json=changes
        )
        res.raise_for_status()
