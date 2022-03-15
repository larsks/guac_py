import click
import logging

LOG = logging.getLogger(__name__)


@click.option("--admin", "-a", is_flag=True)
@click.option("--connection", "-c")
@click.option("--add-perm", multiple=True)
@click.option("--remove-perm", multiple=True)
@click.argument("groupname")
@click.pass_obj
def permissions(
    api,
    admin,
    connection,
    add_perm,
    remove_perm,
    groupname,
):
    add_perm = list(add_perm)
    remove_perm = list(remove_perm)

    if connection:
        conn = api.connection_find(connection)
        LOG.warning("set permissions for group %s connection %s", groupname, conn.name)
        api.group_set_connection_permissions(
            groupname, conn.id, add=add_perm, remove=remove_perm
        )
    else:
        if admin:
            add_perm.append("ADMINISTER")
        LOG.warning("set permissions for group %s", groupname)
        api.group_set_system_permissions(groupname, add=add_perm, remove=remove_perm)
