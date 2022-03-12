import guac.cmd.connection_list


def init_commands(connection):
    connection.command()(guac.cmd.connection_list.list)
