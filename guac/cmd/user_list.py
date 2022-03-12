import click


@click.pass_obj
def list(api):
    for user in api.user_list():
        print(user["username"])
