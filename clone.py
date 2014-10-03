import pickle
import subprocess
import threading

NUMBER_OF_THREADS = 16
URL = "https://bitbucket.org/"

def clone(start, step, repo_list):
    # For every repo available to this thread
    for i in range(start, start + step):
        # Get the version control type
        vct = repo_list[i][0]
        # Get repo's username/name pair
        fullname = repo_list[i][1]
        if vct == 'hg':
            subprocess.check_output(['hg', 'clone', '-U', URL + fullname])
        else:
            subprocess.check_output(['git', 'clone', '--mirror', URL + fullname])

repo_list = pickle.load(open('team5_repos', 'r'))
threads = []
for thread_number in range(NUMBER_OF_THREADS):
    step = len(repo_list) / NUMBER_OF_THREADS
    t = threading.Thread(target=clone, args=(thread_number*step, step, repo_list))
    t.start()
    threads.append(t)
    
for thread in threads:
    thread.join()

