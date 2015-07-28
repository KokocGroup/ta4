from fabric.api import local, task, quiet


def increment_version(index):
    version_row = local("grep 'VERSION = ' setup.py", capture=True)
    version = version_row.split(' = ')[1].strip()
    version = version[1:-1].split('.')
    version[index] = str(int(version[index]) + 1)
    new_version = '.'.join(version)
    local("sed -isetup.py 's/VERSION =.*/VERSION = \"{}\"/g' setup.py".format(new_version))
    return new_version


def release(new_version):
    with quiet():
        local('git commit -am "new version {}"'.format(new_version))
        local('git tag -a v{0} -m \'new version {0}\''.format(new_version))
        local('git push origin master --tags')
    local("python setup.py register")
    local("python setup.py sdist upload -r pypi")


@task
def major():
    release(increment_version(0))


@task
def minor():
    release(increment_version(1))


@task
def patch():
    release(increment_version(2))
