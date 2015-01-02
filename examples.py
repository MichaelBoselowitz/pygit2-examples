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
        test_fp = open(os.path.join(repo.workdir, 'test.txt'), 'w')
        test_fp.write('Version %d.\n' % (version))
        repo.index.add(os.path.basename(test_fp.name))
        test_fp.close()

        user = repo.default_signature
        tree = repo.index.write_tree()
        commit = repo.create_commit('HEAD',
                                    user,
                                    user,
                                    'Version %d of test.txt' % (version),
                                    tree,
                                    parent)
        parent = [commit]
        version += 1
    
# Repo init
# Initialize new remote repo
remote_repo = pygit2.init_repository(REMOTE_REPO, False)
create_commits(remote_repo, 3)


# Clone local repo
local_repo = pygit2.clone_repository(REMOTE_REPO,
                                     LOCAL_REPO)

# Repo pull fastforwardable
create_commits(remote_repo, 2)
for remote in local_repo.remotes:
    if remote.name == 'origin':
        remote.fetch()
        remote_master_id = local_repo.lookup_reference('refs/remotes/origin/master').target
        merge_result, _ = local_repo.merge_analysis(remote_master_id)
        # We can just fastforward
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
            local_repo.head.set_target(remote_master_id)
            local_repo.checkout_head()
        else:
            print 'Should _not_ be here'

# Repo pull merge necessary
create_commits(remote_repo, 1)
create_commits(local_repo, 1)
for remote in local_repo.remotes:
    if remote.name == 'origin':
        remote.fetch()
        remote_master_id = local_repo.lookup_reference('refs/remotes/origin/master').target
        merge_result, _ = local_repo.merge_analysis(remote_master_id)
        # We can just fastforward
        if merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
            local_repo.merge(remote_master_id)
            if local_repo.index.conflicts is not None:
                print 'Oh fuck.'
                sys.exit(-1)

            user = local_repo.default_signature
            tree = local_repo.index.write_tree()
            commit = local_repo.create_commit('HEAD',
                                              user,
                                              user,
                                              'Merge!',
                                              tree,
                                              [local_repo.head.target, remote_master_id])
        else:
            print 'Should _not_ be here'
        

# Repo push

# Create commit

# Export files

# Merge Conficts?
