import click
import dotenv
import logging

import guac.api
import guac.models

import guac.cmd.list_users
import guac.cmd.list_connections
import guac.cmd.add_user
import guac.cmd.delete_user

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


main.command()(guac.cmd.add_user.add_user)
main.command()(guac.cmd.delete_user.delete_user)
main.command()(guac.cmd.list_users.list_users)
main.command()(guac.cmd.list_connections.list_connections)

if __name__ == "__main__":
    main()
