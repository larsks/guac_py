import click


@click.argument("groupname")
@click.pass_obj
def show(api, groupname):
    group = api.group_get(groupname)
    perms = api.group_get_permissions(groupname)
    group.permissions = perms
    print(group.json(indent=2))
