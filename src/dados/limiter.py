from slowapi import Limiter
from slowapi.util import get_remote_address


LIMITE_GET = "20/minutes"

limiter = Limiter(key_func=get_remote_address, default_limits=["5/minutes"])


