import click
import logging
import os
import subprocess
import re

import guac.models
import guac.utils

LOG = logging.getLogger(__name__)


@click.option("--keydir", "-k", default="keys")
@click.option("--recreate-password", "--rp", is_flag=True)
@click.option("--recreate-key", "--rk", is_flag=True)
@click.option("--recreate-user", "--ru", is_flag=True)
@click.option("--recreate-connection", "--rc", is_flag=True)
@click.argument("username")
@click.pass_obj
def add_user(
    api,
    keydir,
    recreate_password,
    recreate_key,
    recreate_user,
    recreate_connection,
    username,
):
    password_file = os.path.join(keydir, f"{username}.password")
    if not os.path.exists(password_file) or recreate_password:
        LOG.warning("creating password for user %s", username)
        with open(password_file, "w") as fd:
            fd.write(guac.utils.random_string(25))
            fd.write("\n")

    with open(password_file) as fd:
        password = fd.read().strip()

    if not os.path.exists(os.path.join(keydir, username)) or recreate_key:
        LOG.warning("creating key for user %s", username)
        try:
            os.remove(os.path.join(keydir, username))
        except FileNotFoundError:
            pass

        subprocess.run(
            [
                "ssh-keygen",
                "-t",
                "rsa",
                "-m",
                "pem",
                "-b",
                "4096",
                "-N",
                "",
                "-f",
                username,
            ],
            cwd=keydir,
            check=True,
            capture_output=True,
        )

    with open(os.path.join(keydir, username)) as fd:
        ssh_private = fd.read()

    if not api.user_exists(username) or recreate_user:
        LOG.warning("creating user %s", username)
        api.user_delete(username)
        if not api.user_add(username):
            raise click.ClickException(f"failed to add user {username}")

    slug = re.sub("[^a-z0-9-]+", "-", username)

    ssh_connection_name = f"{slug}-vm-ssh"
    rdp_connection_name = f"{slug}-vm-rdp"
    if not api.connection_exists(ssh_connection_name) or recreate_connection:
        LOG.warning("add ssh connection %s", ssh_connection_name)
        api.connection_delete(ssh_connection_name)
        c = guac.models.Connection(
            name=ssh_connection_name,
            protocol="ssh",
            parameters=guac.models.SSHConnectionParameters(
                hostname=f"{slug}-vm-int",
                private_key=ssh_private,
                username="fedora",
            ),
        )
        api.connection_add(c.dict(by_alias=True))

    if not api.connection_exists(rdp_connection_name) or recreate_connection:
        LOG.warning("add rdp connection %s", rdp_connection_name)
        api.connection_delete(rdp_connection_name)
        c = guac.models.Connection(
            name=rdp_connection_name,
            protocol="rdp",
            parameters=guac.models.RDPConnectionParameters(
                hostname=f"{slug}-vm-int",
                username="fedora",
                password=password,
            ),
        )
        api.connection_add(c.dict(by_alias=True))

    api.user_grant_connection(username, ssh_connection_name)
    api.user_grant_connection(username, rdp_connection_name)
