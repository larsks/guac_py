import click
import code


@click.pass_obj
def shell(api):
    code.interact(banner="Guacamole API is available as 'api'", local=locals())


def init_commands(parent):
    parent.command()(shell)
