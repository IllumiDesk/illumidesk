from nbgrader.auth import JupyterHubAuthPlugin


c = get_config()

c.Exchange.path_includes_course = True
c.Exchange.root = '/srv/nbgrader/exchange'
c.Authenticator.plugin_class = JupyterHubAuthPlugin
c.Application.log_level = 30
