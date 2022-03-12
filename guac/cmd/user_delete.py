import click
import logging
import re


LOG = logging.getLogger(__name__)


@click.argument("username")
@click.pass_obj
def delete(api, username):
    slug = re.sub("[^a-z0-9-]+", "-", username)
    ssh_connection_name = f"{slug}-vm-ssh"
    rdp_connection_name = f"{slug}-vm-rdp"

    LOG.warning("delete user %s", username)
    api.user_delete(username)

    for conname in [ssh_connection_name, rdp_connection_name]:
        LOG.warning("delete connection %s", conname)
        api.connection_delete(conname)
    api.connection_delete(rdp_connection_name)
