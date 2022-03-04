import random
import string


def random_string(stringlen: int):
    return "".join(
        random.choice(string.ascii_letters + string.digits + "!@#$%^&*.,></?;:[]{}")
        for i in range(stringlen)
    )
