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
        print 'Writing to %s on %s repo' % (test_fp.name, repo)
        test_fp.write('Version %d.\n' % (version))
        # Make sure it was written to disk before moving on.
        test_fp.flush()
        os.fsync(test_fp.fileno())
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
        # Apparently the index needs to be written after a write tree to clean it up.
        # https://github.com/libgit2/pygit2/issues/370
        repo.index.write()
        parent = [commit]
        version += 1


def pull(repo, remote_name='origin'):
    for remote in repo.remotes:
        if remote.name == remote_name:
            remote.fetch()
            remote_master_id = repo.lookup_reference('refs/remotes/origin/master').target
            merge_result, _ = repo.merge_analysis(remote_master_id)
            # Up to date, do nothing
            if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                return
            # We can just fastforward
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                repo.checkout_tree(repo.get(remote_master_id))
                master_ref = repo.lookup_reference('refs/heads/master')
                master_ref.set_target(remote_master_id)
                repo.head.set_target(remote_master_id)
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
                repo.merge(remote_master_id)
                print repo.index.conflicts

                assert repo.index.conflicts is None, 'Conflicts, ahhhh!'
                user = repo.default_signature
                tree = repo.index.write_tree()
                commit = repo.create_commit('HEAD',
                                            user,
                                            user,
                                            'Merge!',
                                            tree,
                                            [repo.head.target, remote_master_id])
                repo.state_cleanup()
            else:
                raise AssertionError('Unknown merge analysis result')


if __name__ == '__main__':
    # Cleanup
    if os.path.exists(LOCAL_REPO):
        shutil.rmtree(LOCAL_REPO)

    if os.path.exists(REMOTE_REPO):
        shutil.rmtree(REMOTE_REPO)


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
