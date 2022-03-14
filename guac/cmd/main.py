import click
import dotenv
import logging

import guac.api
import guac.models

import guac.cmd.user as cmd_user
import guac.cmd.group as cmd_group
import guac.cmd.connection as cmd_connection
import guac.cmd.shell as cmd_shell
import guac.cmd.vm as cmd_vm

dotenv.load_dotenv()

LOG = logging.getLogger(__name__)


@click.group(context_settings={"auto_envvar_prefix": "GUAC"})
@click.option("-v", "--verbose", count=True)
@click.option("--baseurl")
@click.option("--username", default="guacadmin")
@click.option("--password")
@click.pass_context
def main(ctx, verbose, baseurl, username, password):
    loglevel = ["WARNING", "INFO", "DEBUG"][min(verbose, 2)]
    logging.basicConfig(level=loglevel)

    g = guac.api.Guacamole(baseurl, username=username, password=password)
    ctx.obj = g


@main.group()
def user():
    pass


@main.group()
def group():
    pass


@main.group()
def connection():
    pass


@main.group()
def vm():
    pass


cmd_group.init_commands(group)
cmd_user.init_commands(user)
cmd_connection.init_commands(connection)
cmd_shell.init_commands(main)
cmd_vm.init_commands(vm)

if __name__ == "__main__":
    main()
