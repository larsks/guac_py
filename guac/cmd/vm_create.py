import click
import jinja2
import logging
import os
import subprocess
import yaml

import guac.utils

LOG = logging.getLogger(__name__)


@click.option("--keydir", "-k", default="keys")
@click.option("--recreate", "-r", is_flag=True)
@click.option("--namespace", "-n", default="default", envvar="GUAC_VM_NAMESPACE")
@click.option("--templates", "-T", envvar="GUAC_VM_TEMPLATES")
@click.argument("username")
@click.pass_obj
def create(
    api,
    keydir,
    recreate,
    namespace,
    templates,
    username,
):
    objs = []
    password_file = os.path.join(keydir, f"{username}.password")
    sshkey_file = os.path.join(keydir, username)
    slug = guac.utils.slug_from_name(username)

    if templates:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates))
    else:
        env = jinja2.Environment(loader=jinja2.PackageLoader("guac"))

    args = {
        "NAME": slug,
        "NAMESPACE": namespace,
        "ROOTDISK": {
            "SIZE": "10Gi",
            "SOURCE": "shaw-virtual-desktop",
            "NAMESPACE": namespace,
        },
    }

    try:
        with open(password_file) as fd:
            args["CLOUD_USER_PASSWORD"] = fd.read().strip()
    except Exception as err:
        raise click.ClickException(
            f"unable to read password from file {password_file}: {err}"
        )

    try:
        with open(f"{sshkey_file}.pub") as fd:
            args["SSH_PUBLIC_KEY"] = fd.read().strip()
    except Exception as err:
        raise click.ClickException(
            f"unable to read ssh key from file {sshkey_file}.pub: {err}"
        )

    for tname in env.list_templates():
        template = env.get_template(tname)
        objs.append(yaml.safe_load(template.render(**args)))

    if recreate:
        LOG.info(
            "deleting virtual machine resources for %s in namespace %s",
            username,
            namespace,
        )
        try:
            subprocess.run(
                ["kubectl", "delete", "-n", namespace, "-f", "-"],
                check=True,
                stderr=subprocess.PIPE,
                input=yaml.safe_dump_all(objs).encode(),
            )
        except subprocess.CalledProcessError as err:
            LOG.warning(
                "failed to delete resources (ignoring): %s",
                err.stderr.decode().splitlines(),
            )

    try:
        LOG.info(
            "creating virtual machines resources for %s in namespace %s",
            username,
            namespace,
        )
        subprocess.run(
            ["kubectl", "apply", "-n", namespace, "-f", "-"],
            check=True,
            stderr=subprocess.PIPE,
            input=yaml.safe_dump_all(objs).encode(),
        )
    except subprocess.CalledProcessError as err:
        LOG.fatal(
            "failed to create vm: %s",
            err.stderr.decode().splitlines(),
        )
        raise click.Abort()
