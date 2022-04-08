import guac.cmd.group_create
import guac.cmd.group_permissions
import guac.cmd.group_list
import guac.cmd.group_delete
import guac.cmd.group_show


def init_commands(group):
    group.command()(guac.cmd.group_create.create)
    group.command()(guac.cmd.group_permissions.permissions)
    group.command()(guac.cmd.group_list.list)
    group.command()(guac.cmd.group_delete.delete)
    group.command()(guac.cmd.group_show.show)
