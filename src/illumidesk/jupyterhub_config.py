""" Configuration file for jupyterhub. """
import os

from dotenv import load_dotenv
from oauthenticator.generic import GenericOAuthenticator

load_dotenv()


c.JupyterHub.allow_root = True
c.JupyterHub.allow_origin = "*"

# Set port and IP
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.port = 8000

# Set log level
c.Application.log_level = "DEBUG"

# Header settings for iFrame and SameSite
c.JupyterHub.tornado_settings = {
    "headers": {"Content-Security-Policy": "frame-ancestors 'self' *"},
    "cookie_options": {"SameSite": "None", "Secure": True},
}

# Upgrade the database automatically on start
c.JupyterHub.upgrade_db = True

# JupyterHub Postgres connection URI
postgres_user = os.environ.get("POSTGRES_USER") or "jupyterhub"
postgres_password = os.environ.get("POSTGRES_PASSWORD") or "jupyterhub"
postgres_host = os.environ.get("POSTGRES_HOST") or "postgres"
postgres_port = os.environ.get("POSTGRES_PORT") or "5432"
postgres_db = os.environ.get("POSTGRES_DB") or "jupyterhub"
c.JupyterHub.db_url = f"postgres://{postgres_user}:{postgres_password}/{postgres_host}:{postgres_port}/{postgres_db}"

# Set the authenticator
c.JupyterHub.authenticator_class = GenericOAuthenticator

c.Authenticator.admin_users = {"admin"}
c.Authenticator.auto_login = True
c.Authenticator.allowed_users = {"greg", "abhi", "greg@example.com"}

# Verify TLS certificates.
if os.environ.get("OAUTH2_TLS_VERIFY") == "True":
    c.OAuthenticator.tls_verify = True
else:
    c.OAuthenticator.tls_verify = False

# OAuthenticator settings for OAuth2
c.OAuthenticator.client_id = os.environ.get("OAUTH_CLIENT_ID") or "illumidesk-hub"
c.OAuthenticator.client_secret = os.environ.get("OAUTH_CLIENT_SECRET")
c.OAuthenticator.oauth_callback_url = (
    os.environ.get("OAUTH_CALLBACK_URL") or "http://127.0.0.1/hub/oauth_callback"
)
c.OAuthenticator.authorize_url = (
    os.environ.get("OAUTH2_AUTHORIZE_URL")
    or "http://127.0.0.1/auth/realms/illumidesk-realm/protocol/openid-connect/auth"
)
c.OAuthenticator.token_url = (
    os.environ.get("OAUTH2_TOKEN_URL")
    or "http://127.0.0.1/auth/realms/illumidesk-realm/protocol/openid-connect/token"
)
c.OAuthenticator.enable_auth_state = True

# Login service name
c.GenericOAuthenticator.login_service = (
    os.environ.get("GENERICAUTH_LOGIN_SERVICE_NAME") or "Keycloak"
)
# TODO: clarify scopes
c.GenericOAuthenticator.scope = ["openid"]
c.GenericOAuthenticator.userdata_url = (
    os.environ.get("OAUTH2_USERDATA_URL")
    or "http://localhost:8080/auth/realms/illumidesk-realm/protocol/openid-connect/userinfo"
)
c.GenericOAuthenticator.userdata_method = (
    os.environ.get("GENERICAUTH_USERDATA_METHOD") or "GET"
)
c.GenericOAuthenticator.userdata_params = {"state": "state"}
c.GenericOAuthenticator.username_key = (
    os.environ.get("OAUTH2_USERNAME_KEY") or "preferred_username"
)
