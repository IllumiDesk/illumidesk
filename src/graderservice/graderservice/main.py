import logging
import sys

from graderservice import create_app

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
