from fabric.api import env, local

env.exclude_requirements = set([
    'nose', 'coverage'
])

def freeze():
    """
    pip freeze > requirements.txt, excluding virtualenv clutter
    """
    reqs = local('pip freeze', capture=True).split('\n')
    reqs = [r for r in reqs if r.split('==')[0] not in env.exclude_requirements]
    reqs = '\n'.join(reqs)

    with open('requirements.txt', 'wb') as f:
        f.write(reqs)

    print(reqs)

