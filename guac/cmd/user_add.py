import click
import logging
import os

import guac.models
import guac.utils

LOG = logging.getLogger(__name__)


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
    password = guac.utils.generate_password(
        username, password_file, recreate=recreate_password
    )

    sshkey_file = os.path.join(keydir, username)
    ssh_private, ssh_public = guac.utils.generate_keypair(
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
