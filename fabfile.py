from fabric.api import cd, env, local, sudo

_INTERNAL_REPO = 'http://our.fogbugz.com/kiln/Repo/Kiln/Experiments/ILoveMercurial'
_EXTERNAL_REPO = 'ssh://hg@bitquabit.com/ilhg'

def bqb():
    env.hosts = ['bitquabit.com']

def _update_repo(repo, rev='tip'):
    with cd(repo):
        ctx = local('hg id %s' % _INTERNAL_REPO, capture=True)
        local('hg push -r %s %s' % (ctx, _EXTERNAL_REPO))
        sudo('hg pull', user='www-data')
        sudo('hg up -C %s' % rev, user='www-data')

def deploy(rev='tip'):
    path = '/var/www/flask/ilhg'
    _update_repo(path, rev)
    sudo('killall -s SIGHUP uwsgi')
