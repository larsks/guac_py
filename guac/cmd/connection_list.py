import click


@click.pass_obj
def list(api):
    for conn in api.connection_list():
        print(conn.id, conn.name)
