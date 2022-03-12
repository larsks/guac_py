import click
import logging


LOG = logging.getLogger(__name__)


@click.argument("groupname")
@click.pass_obj
def delete(api, groupname):
    LOG.warning("delete group %s", groupname)
    api.group_delete(groupname)
