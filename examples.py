import os
import sys
import shutil
import pygit2

SSH_KEY_PUBLIC = os.path.expanduser('~/.ssh/id_rsa.pub')
SSH_KEY_PRIVATE = os.path.expanduser('~/.ssh/id_rsa_unencrypted')
CREDENTIALS = pygit2.credentials.Keypair('git',
                                         SSH_KEY_PUBLIC,
                                         SSH_KEY_PRIVATE,
                                         None)
REMOTE_REPO = 'remote_repo'
LOCAL_REPO = 'local_repo'

# Cleanup
if os.path.exists(LOCAL_REPO):
    shutil.rmtree(LOCAL_REPO)

if os.path.exists(REMOTE_REPO):
    shutil.rmtree(REMOTE_REPO)

version = 1
def create_commits(repo, how_many):
    if repo.head_is_unborn:
        parent = []
    else:
        parent = [repo.head.target]

    global version
    for i in range(how_many):
        test_fp = open(os.path.join(repo.workdir,
                                    os.path.basename(os.path.normpath(repo.workdir)) + '_test.txt'), 'a+')
        test_fp.write('Version %d.\n\n' % (version))
        test_fp.close()
        repo.index.add_all()

        user = repo.default_signature
        tree = repo.index.write_tree()
        commit = repo.create_commit('HEAD',
                                    user,
                                    user,
                                    'Version %d of test.txt on %s' % (version, os.path.basename(os.path.normpath(repo.workdir))),
                                    tree,
                                    parent)
        parent = [commit]
        version += 1
    
# Repo init
# Initialize new remote repo
remote_repo = pygit2.init_repository(REMOTE_REPO, False)
create_commits(remote_repo, 1)

# Clone local repo
local_repo = pygit2.clone_repository(REMOTE_REPO,
                                     LOCAL_REPO)

# Repo pull fastforwardable
create_commits(remote_repo, 1)
pull(local_repo)

# Repo pull merge necessary
# create_commits(local_repo, 1)
# create_commits(remote_repo, 1)

# pull(local_repo)


# Repo push

# Create commit

# Export files

# Merge Conficts?
