# guac_py: Tools for interacting with the Guacamole REST API

The `guac` command provides a collection of subcommands for managing resources in [Guacamole][].

[Guacamole]: https://guacamole.apache.org/doc/gug/index.html

## Configuration

In order to interact with your Guacamole service, this tool needs to know:

- The base URL for the API endpoint
- A username
- A password

These can all be provided on the command line (`--baseurl`, `--username`, and `--password`) or via environment variables (`GUAC_BASEURL`, `GUAC_USERNAME`, and `GUAC_PASSWORD`).

## Additional documentation

- [Guacamole documentation](https://guacamole.apache.org/doc/gug/index.html)
- [Guacamole REST API](https://github.com/ridvanaltun/guacamole-rest-api-documentation)

