import logging
import os
import random
import re
import string
import subprocess

LOG = logging.getLogger(__name__)


def random_string(stringlen: int):
    return "".join(
        random.choice(string.ascii_letters + string.digits + "!@#$%^&*.,></?;:[]{}")
        for i in range(stringlen)
    )


def slug_from_name(name):
    slug = re.sub("[^a-z0-9-]+", "-", name)
    slug = re.sub("-+", "-", slug)

    return slug


def generate_password(username, password_file, recreate=False):
    if not os.path.exists(password_file) or recreate:
        LOG.warning("creating password for user %s", username)
        with open(password_file, "w") as fd:
            fd.write(random_string(25))
            fd.write("\n")

    with open(password_file) as fd:
        password = fd.read().strip()

    return password


def generate_keypair(username, sshkey_file, recreate=False):
    if not os.path.exists(sshkey_file) or recreate:
        LOG.warning("creating key for user %s", username)
        try:
            os.remove(sshkey_file)
        except FileNotFoundError:
            pass

        subprocess.run(
            [
                "ssh-keygen",
                "-t",
                "rsa",
                "-m",
                "pem",
                "-b",
                "4096",
                "-N",
                "",
                "-f",
                sshkey_file,
            ],
            check=True,
            capture_output=True,
        )

    with open(sshkey_file) as fd:
        ssh_private = fd.read()

    with open(f"{sshkey_file}.pub") as fd:
        ssh_public = fd.read()

    return ssh_private, ssh_public
