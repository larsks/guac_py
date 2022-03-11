import click


@click.pass_obj
def list_groups(api):
    for group in api.group_list():
        print(group["identifier"])
