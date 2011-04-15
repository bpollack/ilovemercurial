from fabric.api import cd, env, sudo

def bqb():
    env.hosts = ['bitquabit.com']

def _update_repo(repo, rev='tip'):
    with cd(repo):
        sudo('hg pull', user='www-data')
        sudo('hg up -C %s' % rev, user='www-data')

def deploy(rev='tip'):
    path = '/var/www/flask/ilhg'
    _update_repo(path, rev)
    sudo('killall -s SIGHUP uwsgi')
