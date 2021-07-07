""" Configuration file for jupyterhub. This version is used primarily for testing. """
from illumidesk.authenticators.authenticator import IllumiDeskDummyAuthenticator

# # Set port and IP
c.JupyterHub.ip = "0.0.0.0"
c.JupyterHub.port = 8000

# # Set log level
c.Application.log_level = "DEBUG"

# Header settings for iFrame and SameSite
c.JupyterHub.tornado_settings = {
    "headers": {"Content-Security-Policy": "frame-ancestors 'self' *"},
    "cookie_options": {"SameSite": "None", "Secure": True},
}

# Upgrade the database automatically on start
c.JupyterHub.upgrade_db = True

# Set the authenticator
c.JupyterHub.authenticator_class = IllumiDeskDummyAuthenticator

# Add an admin user for testing the admin page
c.Authenticator.admin_users = {"admin"}

# Enable auth state to pass the authentication dictionary values within auth_state to ths spawner
c.Authenticator.enable_auth_state = True
