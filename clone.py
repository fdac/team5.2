import time
import pickle
import subprocess
import threading
import os

NUMBER_OF_THREADS = 16
URL = "https://bitbucket.org/"
CLONE_DISK = "/media/sdb"
CLONE_DIR = "/media/sdb/clones"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

count = 0;
counter_lock = threading.Lock()
rsync_lock = threading.Lock()

def check_space():
    while True:
        df = subprocess.check_output(['df', CLONE_DISK])
        df = df.split("\n")[1].split()
        if int(df[4][0:-1]) > 80:
            with rsync_lock:
                rsync = subprocess.Popen("rsync -ae 'ssh -p 2200' --delete " + CLONE_DIR + " mahmadza@da2.eecs.utk.edu:", shell=True)
                print rsync.communicate()
        time.sleep(20)

def clone(start, step, repo_list):
    global count
    repo_len = len(repo_list)
    # For every repo available to this thread
    for i in range(start, min(start + step, repo_len)):
        # Get the version control type
        vct = repo_list[i][0]
        # Get repo's username/name pair
        fullname = repo_list[i][1]
        # Determine versioning system and run cloning in silent mode
        if vct == 'hg':
            process_command = ['hg', 'clone', '-U', URL + fullname, fullname.replace("/", "~"), '-q']
        else:
            process_command = ['git', 'clone', '--mirror', URL + fullname, fullname.replace("/", "~"), '--quiet']
        try:
            # Run a subprocess that clones, if we're not running rsync
            while rsync_lock.locked():
                time.sleep(0.1)
            cloning_agent = subprocess.Popen(process_command)
            cloning_agent.communicate()
            with counter_lock:
                count+=1
        except subprocess.CalledProcessError as ex:
            pass

        print "Number of repos cloned: %d\r"%count,

if __name__ == "__main__":
    # Make a directory to put everything inside
    try:
        os.mkdir(CLONE_DIR)
    except:
        pass
    os.chdir(CLONE_DIR)

    # Read the list of repos to clone
    repo_list = pickle.load(open(CURRENT_DIR + '/team5_repos', 'r'))
    threads = []
    for thread_number in range(NUMBER_OF_THREADS - 1):
        # Divide the list and start Daemon threads
        step = len(repo_list) / NUMBER_OF_THREADS
        t = threading.Thread(target=clone, args=(thread_number*step, step, repo_list))
        t.setDaemon(True)
        t.start()
        threads.append(t)

    # Start another thread solely for checking storage space
    t = threading.Thread(target=check_space)
    t.setDaemon(True)
    t.start()
    threads.append(t)
    
    while threading.active_count() > 0:
        time.sleep(0.1)

