import click
import logging

LOG = logging.getLogger(__name__)


@click.option("--admin", "-a", is_flag=True)
@click.argument("groupname")
@click.pass_obj
def add(
    api,
    admin,
    groupname,
):
    LOG.warning("create group %s", groupname)
    api.group_add(groupname)
    if admin:
        api.group_set_permissions(groupname, perms=["ADMINISTER"])
