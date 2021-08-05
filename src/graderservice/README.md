# IllumiDesk's Grader Setup Service

## Overview

Microservice used to setup new shared grader notebooks.

## Dev Install

Install in editable mode:

    pip install -e .

## Run Application

Run application locally with debug mode enabled:

```bash
export FLASK_APP=graderservice
export FLASK_ENV=development
flask run
```

> **Note**: the service does require environment variables however all have defaults. You can set your own values by using the `export <env-var-here>=<env-var-value>` before starting the application. You can also set environment variables with the docker run command.

## Update Dependencies

    pip-compile requirements.in

## Environment Variables

| Environment Variable | Description | Type | Default Value |
| --- | --- | --- | --- |
| GRADER_IMAGE_NAME | The shared grader notebook image:tag | `string` | `illumidesk/grader-notebook:latest` |
| GRADER_IMAGE_PULL_POLICY | The shared grader notebook image pull policy | `string` | `IfNotPresent` |
| GRADER_PVC | The Kubernetes PVC for the grader setup service | `string` | `grader-setup-pvc` |
| GRADER_SHARED_PVC | The shared grader notebook PVC for the exchange directory | `string` | `exchange-shared-volume` |
| GRADER_REQUESTS_MEM | The guaranteed amount of memory (RAM). | `string` | `""` |
| GRADER_REQUESTS_CPU | The guaranteed CPU. | `string` | `""` |
| GRADER_LIMITS_MEM | The upper bound memory (RAM) limit. | `string` | `"4G"` |
| GRADER_LIMITS_CPU | The upper bound CPU limit. | `string` | `"2000m"` |
| ILLUMIDESK_MNT_ROOT | Root directory for `{org_name}/grader-{course_id}` | `string` | `/illumidesk-courses` |
| ILLUMIDESK_NB_EXCHANGE_MNT_ROOT | Root directory for `{org_name}/exchange` | `string` | `/illumidesk-nb-exchange` |
| IS_DEBUG | Sets the debug option to True or False for the Kubernetes client and the shared grader notebook | `bool` | `True` |
| NAMESPACE | The Kubernetes namespace name | `string` | `default` |
| NB_UID | The user's uid that owns the shared grader home directory | `string` | `10001` |
| NB_GID | The user's gid that owns the shared grader home directory | `string` | `100` |

## License

Apache 2.0
