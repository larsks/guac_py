import click


@click.pass_obj
def list(api):
    for group in api.group_list():
        print(group.identifier)
