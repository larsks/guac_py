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

## EXAMPLES

### Adding a user

```
guac user add alice@example.com
```

This will generate a password and an ssh key pair in `keydir` (by default `./keys`), and use those to create two connections:

- `alice-example-com-vm-rdp`
- `alice-example-com-vm-ssh`

### Create user virtual machine

```
guac vm create alice@example.com -n shaw-virtual-desktop
```

This will use `kubectl` to create resources from the templates embedded in the `guac` package. This includes:

- A `userdata-alice-example-com` secret that provides the ssh public key and user password to `cloud-init` when the vm boots,
- A `alice-example-com-vm-int` service that exposes the RDP and SSH ports, and
- A `alice-example-com-vm` virtual machine

You will need to specify the namespace in which to operate using the `-n` option or by setting the
`GUAC_VM_NAMESPACE` environment variable.

### Recreate user virtual machine

If a virtual machine has become inoperative:

```
guac vm create --recreate alice@example.com -n shaw-virtual-desktop
```

This will first delete the associated resources, and then re-create them as described in the previous example.

You will need to specify the namespace in which to operate using the `-n` option or by setting the
`GUAC_VM_NAMESPACE` environment variable.

### Recreate user credentials

```
guac user rekey alice@example.com
```

This will regenerate the ssh keypair and password for `alice@example.com`:

- Update the associated files in the `keys/` directory
- Recreate the Guacamole connections with the new values
