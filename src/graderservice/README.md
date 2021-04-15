# IllumiDesk's Grader Setup Service

## Overview

Microservice used to setup new shared grader notebooks.

## Dev Install

Install in editable mode:

    pip install -e .

## Run Application

Run application locally with debug mode enabled:

```bash
export FLASK_APP=src/graderservice/graderservice
export FLASK_ENV=development
flask run
```

## Update Dependencies

    pip-compile requirements.in
