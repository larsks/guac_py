import click
import jinja2
import logging
import subprocess
import yaml

import guac.utils

LOG = logging.getLogger(__name__)


@click.option("--namespace", "-n", default="default", envvar="GUAC_VM_NAMESPACE")
@click.option("--templates", "-T", envvar="GUAC_VM_TEMPLATES")
@click.argument("username")
@click.pass_obj
def delete(
    api,
    namespace,
    templates,
    username,
):
    objs = []
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
        "CLOUD_USER_PASSWORD": "",
        "SSH_PUBLIC_KEY": "",
    }

    for tname in env.list_templates():
        template = env.get_template(tname)
        objs.append(yaml.safe_load(template.render(**args)))

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
        LOG.error(
            "failed to delete resources: %s",
            err.stderr.decode().splitlines(),
        )
        raise click.Abort()
