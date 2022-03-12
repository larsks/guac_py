import guac.cmd.user_add
import guac.cmd.user_delete
import guac.cmd.user_list


def init_commands(user):
    user.command()(guac.cmd.user_add.add)
    user.command()(guac.cmd.user_delete.delete)
    user.command()(guac.cmd.user_list.list)
