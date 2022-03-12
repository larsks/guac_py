import random
import re
import string


def random_string(stringlen: int):
    return "".join(
        random.choice(string.ascii_letters + string.digits + "!@#$%^&*.,></?;:[]{}")
        for i in range(stringlen)
    )


def slug_from_name(name):
    slug = re.sub("[^a-z0-9-]+", "-", name)
    slug = re.sub("-+", "-", slug)

    return slug
