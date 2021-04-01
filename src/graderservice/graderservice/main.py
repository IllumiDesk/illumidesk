import logging.config
from os import path

from graderservice import create_app

log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging_config.ini")
logging.config.fileConfig(log_file_path)
logger = logging.getLogger()


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
