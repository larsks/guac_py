import click


@click.pass_obj
def list_users(api):
    for user in api.user_list():
        print(user["username"])
