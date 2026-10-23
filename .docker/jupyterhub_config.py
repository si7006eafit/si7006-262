"""Local JupyterHub of the development container, for the notebooks of the Spark labs.

One user, the container user, signs in with the password of JUPYTERHUB_PASSWORD (default
bigdatalabs) and gets
JupyterLab on the repository. It listens on port 8888, published only on 127.0.0.1.
"""
import os

c = get_config()  # noqa: F821  (provided by JupyterHub when it loads this file)

USER = os.environ.get('JUPYTERHUB_USER', 'big-data-labs')
STATE = os.path.expanduser('~/.jupyterhub')
os.makedirs(STATE, exist_ok=True)

# Network: the hub listens on every interface of the container, so Docker can publish the port
c.JupyterHub.bind_url = 'http://0.0.0.0:8888'
c.JupyterHub.hub_ip = '127.0.0.1'

# State of the hub: database and cookie secret in the home folder of the container user
c.JupyterHub.db_url = f'sqlite:///{STATE}/jupyterhub.sqlite'
c.JupyterHub.cookie_secret_file = f'{STATE}/jupyterhub_cookie_secret'
c.ConfigurableHTTPProxy.pid_file = f'{STATE}/jupyterhub-proxy.pid'

# Authentication: one local user with a shared password of 8 characters or more
c.JupyterHub.authenticator_class = 'shared-password'
c.SharedPasswordAuthenticator.user_password = os.environ.get('JUPYTERHUB_PASSWORD', 'bigdatalabs')
c.Authenticator.allowed_users = {USER}

# Spawner: the notebook server runs as the same container user, with the repository as its root
c.JupyterHub.spawner_class = 'simple'
c.Spawner.notebook_dir = '/app'
c.Spawner.default_url = '/lab/tree/labs'
c.Spawner.http_timeout = 120
# Variables the labs need inside the notebooks: Java for Spark, PostgreSQL defaults, AWS credentials
c.Spawner.env_keep = [
    'PATH', 'LANG', 'LC_ALL', 'JAVA_HOME', 'PYTHONPATH',
    'PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE',
    'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN',
    'AWS_DEFAULT_REGION', 'AWS_DEFAULT_OUTPUT', 'DEPLOY_APP',
]
# Stop the notebook server after it signs out, so Spark sessions do not linger
c.JupyterHub.shutdown_on_logout = True
