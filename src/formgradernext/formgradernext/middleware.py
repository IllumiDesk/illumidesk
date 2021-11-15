from functools import wraps
from typing import Dict

from tornado.web import RequestHandler


def coop_coep_headers(f):
    """
    Sets the COOP and COEP headers, which are required for cross origin isolation (which unlocks
    certain features in embedded Starboard Notebook frames). These headers need to be present
    all the way down (i.e. in the top level webpage, as well as pages within the iFrame).
    """

    @wraps(f)
    def handle(self: RequestHandler, *args, **kwargs) -> Dict:
        self.set_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.set_header("Cross-Origin-Opener-Policy", "same-origin")
        return f(self, *args, **kwargs)

    return handle
