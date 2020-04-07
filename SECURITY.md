# Security Overview

## Using IllumiDesk Securely

This document provides and overview of how to imporove security for individuals or organizations running the IllumiDesk system using the software artifacts avaiable within this repository. IllumiDesk maintains additional security policies and practices documents which cover the hosted and enterprise versions of the system.

## Upstream Dependencies

Like most systems, IllumiDesk depends on many dependencies to run the system. In particular, IllumiDesk relies on [JupyterHub](https://jupyterhub.readthedocs.io/en/stable/reference/websecurity.html) and the [Tornado](https://www.tornadoweb.org/en/stable/guide/security.html) web server to work correctly. Please refer to the provided links to consider their own security recommendations.

## General Security Recommendations

1. **TSL**: use TSL for all internal and external services. This includes enforcing the use of TSL from clients located outside your network and services that need to communicate with each other within your private network. For example, this setup is not recommended, even though it requires TSL from public facing clients:

    Public Client --> Port 443 --> [Reverse Proxy] --> Port 80 --> [Backend] --> Port 80 --> [Notebooks]

A more secure setups would reflect end-to-end TSL:

    Public Client --> Port 443 --> [Reverse Proxy] --> Port 443 --> [Backend] --> Port 443 --> [Notebooks]

2. **Environment Variables**: several environment variables contain sensitive information, such as database passwords. Never store raw credentials within docker images. When using an environment variables within a running container make sure you store the source of the environment variable value in a secure location and that the running container has the proper permissions to access the encrypted values.

3. **Rotate Keys**: rotate encryption keys whenever possible. For example, keys used to encrypt session cookies should be periodically rotated.

4. **User Credentials**: if you plan on using the system to store credentials from your users then it is recommended to use a trusted third party system to manage the user passwords. For example, you could use an integrated system such as a Learning Management System or a federated identity solution which use the standard OAuth features.

## General Security Policies

IllumiDesk automates security scanning and dependency upgrades throughout the software pipeline wherever possible. These automations include but are not limited to:

- Scan upstream dependencies for security vulnerabilities. If a security vulnerability is found and a patch is available from the upstream dependency, automatically create a Pull Request and alert the repository maintainers.

- Scan docker images after building and pushing the images to the registry.

- Block merges to the master branch which do not pass all tests and/or do not have the sign off from one of the project's maintainers.

- Ensure that all dependencies used for deployments are set to specific releases.

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible receiving such patches depend on the CVSS v3.1 Rating:

| CVSS v3.1 | Supported Versions                        |
| --------- | ----------------------------------------- |
| 9.0-10.0  | Releases within the previous three months |
| 4.0-8.9   | Most recent release                       |

## Reporting a Vulnerability

Please report (suspected) security vulnerabilities to
**[security@illumidesk.com](mailto:security@illumidesk.com)**. You will receive a response from us within 48 hours. If the issue is confirmed, we will release a patch as soon as possible depending on complexity but historically within a few days.

If your disclosure is extremely sensitive, you may choose to encrypt your report using the key below. Please only use this for critical security reports.

```
-----BEGIN PGP PUBLIC KEY BLOCK-----

mQENBF6MvIYBCADH4z0sknM1E5cuFrDeqMI3PbqcqO8pe2bHXNUqCgMAowSkfsrV
AOJ2KyN2xZALoUT7lEpzv6l2c1WomI63pVZ+euvdArfYLYW5S7jKExy2vBRlpElG
N32kKEO9eRFCsv71GeYEhtUE+nlj6hNerkSqfM+Rz+LsqapGizDFAk87iGnsYJzp
N4UZJcngvuUwJgalVn2X3sORo9GcXlHoDQpaoFpU1EVevAX1gseiE99dhv02QBKW
DXPPFxUV3/peGvbRff5TB2ZRxR0cF/pQlBApvTUvPJIOaov+ox8GRwSX0k30DGQk
M/zvx0P7zt9V7lwpBz9U18UGL0WIqeR+14TXABEBAAG0LUlsbHVtaURlc2sgU2Vj
dXJpdHkgPHNlY3VyaXR5QGlsbHVtaWRlc2suY29tPokBVAQTAQgAPhYhBLhd9rZC
GgOQXOGBzLwYMelnOHeDBQJejLyGAhsDBQkDwmcABQsJCAcCBhUKCQgLAgQWAgMB
Ah4BAheAAAoJELwYMelnOHeDYLEH/RVcBq5c02XTF6oqrIs1xGPKYeEty00Mk9yx
PRpoIunxZmmNU3AM3or7QFoYblHTBY/1hU8E7H4OoyVKEC3ZtlyU+fztTAfuxd+p
Nye/pup3mFtda+HoXKyCKZKfymJ5kFS+IVjP1hunFpWwppJsGG7tIvpPILfCAh8n
51jbZwGWk4QheYL6FysZMqLgCAAzzrV9qzuTRL0VGSgzn69XlgvJWXDpZnlCCxxg
AnZ3sw6pbYpWqmyvvSucvLQSC+vk7kkahaw46665iE3vIOmJXbRbDn9VOwx/Xe35
K1iboIRMLsfy1YYgGQ/F+D+T+xDWHQ0lSDJWMjYp/0lqyJn7S7y5AQ0EXoy8hgEI
ALuzU8t1noAOZCCc6GlHR3Fpx79qR5t7mgLtsTcI4oyL1CzC9C9SLGJ/M3H0ES1B
QSxcYhdUgolulSE+MFdopQd/ElNbO8pAb9pIZGtyWGLxRzsXMiLl4ZWcMPJpdM4w
izjw6oP8Fd/V3EomPWEwnLPPZgAPqMGlBqiQTS3iSsqCf6nepmdLi/EPXDLEuq6o
X0nhtWUTFOb4d1Q9xkexx7cyyj5hCLjsysL9G9E2ZT5QJTAltSjEZNmPBN+LpBRv
y742UE/0z8+PYzWFCGisD8I2vLE6VpesNW7ItWXmxz7t98KnwVXSfC0LHJh7kKEb
hTgWGxrE6i471QLCDKyey9MAEQEAAYkBPAQYAQgAJhYhBLhd9rZCGgOQXOGBzLwY
MelnOHeDBQJejLyGAhsMBQkDwmcAAAoJELwYMelnOHeDOdMH/iy7MUpa5HS1UVrn
cGjKL314sJwv+KuZ6YtlEAVf8e4w8YIqenKtGzo3nSIgMTeyffyi58t7D7hmKkjm
kONVorCi4UxISVThLhBEoKuRwYJyjV1FmAOwYIiQd/i2UPLlC7NIJCYMAIHLCSd+
rBcrXbYoX/Kcs99gFOz9F3LTDlg6xrtlzOKP8RD4L/VvE0I5RqBFD593szr35afV
yCJN1iEttNKGI3gvAZw2LafnrFYFoFllTdj+fqCUUXxNrgaciQoKiDYf3MFiRzqX
w8nJkNLb2SfEncY8adlt/uP7N9EwHjzt2uy2oH1lZM0SLI1miXi2zaf2GN8Ri2RC
GWbYxF0=
=hXgw
-----END PGP PUBLIC KEY BLOCK-----
```
