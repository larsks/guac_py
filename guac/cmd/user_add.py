import click
import logging
import os
import subprocess

import guac.models
import guac.utils

LOG = logging.getLogger(__name__)


def generate_password(username, password_file, recreate=False):
    if not os.path.exists(password_file) or recreate:
        LOG.warning("creating password for user %s", username)
        with open(password_file, "w") as fd:
            fd.write(guac.utils.random_string(25))
            fd.write("\n")

    with open(password_file) as fd:
        password = fd.read().strip()

    return password


def generate_keypair(username, sshkey_file, recreate=False):
    if not os.path.exists(sshkey_file) or recreate:
        LOG.warning("creating key for user %s", username)
        try:
            os.remove(sshkey_file)
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
                sshkey_file,
            ],
            check=True,
            capture_output=True,
        )

    with open(sshkey_file) as fd:
        ssh_private = fd.read()

    with open(f"{sshkey_file}.pub") as fd:
        ssh_public = fd.read()

    return ssh_private, ssh_public


@click.option("--keydir", "-k", default="keys")
@click.option("--recreate-password", "--rp", is_flag=True)
@click.option("--recreate-key", "--rk", is_flag=True)
@click.option("--recreate-user", "--ru", is_flag=True)
@click.option("--recreate-connection", "--rc", is_flag=True)
@click.option("--connection-group", "-g")
@click.argument("username")
@click.pass_obj
def add(
    api,
    keydir,
    recreate_password,
    recreate_key,
    recreate_user,
    recreate_connection,
    username,
    connection_group,
):
    password_file = os.path.join(keydir, f"{username}.password")
    password = generate_password(username, password_file, recreate=recreate_password)

    sshkey_file = os.path.join(keydir, username)
    ssh_private, ssh_public = generate_keypair(
        username, sshkey_file, recreate=recreate_key
    )

    if not api.user_exists(username) or recreate_user:
        LOG.warning("creating user %s", username)
        api.user_delete(username)
        if not api.user_add(username):
            raise click.ClickException(f"failed to add user {username}")

    slug = guac.utils.slug_from_name(username)
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
                enable_drive="true",
                create_drive_path="true",
                drive_path=f"/shared/{slug}",
                drive_name="Shared",
            ),
        )
        api.connection_add(c.dict(by_alias=True))

    api.user_grant_connection(username, ssh_connection_name)
    api.user_grant_connection(username, rdp_connection_name)
    if connection_group:
        api.group_add_connection(connection_group, ssh_connection_name)
    if connection_group:
        api.group_add_connection(connection_group, rdp_connection_name)
