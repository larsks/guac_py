import click


@click.pass_obj
def list_connections(api):
    for conn in api.connection_list().values():
        print(conn["name"])
