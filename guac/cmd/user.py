import guac.cmd.user_create
import guac.cmd.user_delete
import guac.cmd.user_list
import guac.cmd.user_rekey


def init_commands(user):
    user.command()(guac.cmd.user_create.create)
    user.command()(guac.cmd.user_delete.delete)
    user.command()(guac.cmd.user_list.list)
    user.command()(guac.cmd.user_rekey.rekey)
