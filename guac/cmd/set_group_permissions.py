import click
import logging

LOG = logging.getLogger(__name__)


@click.option("--admin", "-a", is_flag=True)
@click.option("--add-perm", multiple=True)
@click.option("--remove-perm", multiple=True)
@click.argument("groupname")
@click.pass_obj
def set_group_permissions(
    api,
    admin,
    add_perm,
    remove_perm,
    groupname,
):
    add_perm = list(add_perm)
    remove_perm = list(remove_perm)

    if admin:
        add_perm.append("ADMINISTER")

    LOG.warning("set permissions for group %s", groupname)
    api.group_set_permissions(groupname, add=add_perm, remove=remove_perm)
