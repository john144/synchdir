import synchdir
from filecmp import dircmp
import os
import shutil
import queue
import threading
import time


class PrintHandlerThread(threading.Thread):
    #  Print messages when using main
    def __init__(self, msg_queue):
        super(PrintHandlerThread, self).__init__()
        self._stop_event = threading.Event()
        self.msg_queue = msg_queue

    def run(self):
        # Check  if there is a new message in the queue to display
        while not self._stop_event.is_set():
            try:
                record = self.msg_queue.get(True, 0.05)
                print(record)
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self._stop_event.set()
        super(PrintHandlerThread, self).join(timeout)


def print_diff_files(dcmp):
    for name in dcmp.diff_files:
        print("diff_file %s found in %s and %s" % (name, dcmp.left, dcmp.right))
    for sub_dcmp in dcmp.subdirs.values():
        print_diff_files(sub_dcmp)


def run_test_case(test_root, test_case, model_folder, src, dst):
    # Set up the necessary folders
    model = os.path.join(test_root, test_case, model_folder)
    test = os.path.join(test_root, test_case, "test")
    sync_src = os.path.join(test_root, test_case, "test", src)
    sync_dst = os.path.join(test_root, test_case, "test", dst)

    print("\nTest parameters:\n")
    print("model:", model)
    print("test:", test)
    print("sync_src:", sync_src)
    print("sync_dst:", sync_dst)

    # Make sure the model folder exists
    assert(os.path.exists(model))

    # If the test folder exists,  remove it and replace with fresh copy from model
    print("\nInitializing folders:\n")
    if os.path.exists(test):
        print(f"Removing {test}")
        shutil.rmtree(test)
    shutil.copytree(model, test)

    # Run the test
    print("\nRunning the test:\n")
    synchdir.synchdir(msg_queue, sync_src, sync_dst)

    # Make sure we haven't changed the source folder
    print("\nTest that source folder is unchanged:\n")
    dcmp = dircmp(os.path.join(model, src), sync_src)
    print_diff_files(dcmp)

    # Make sure source and dest are in synch
    print("\nTest that source and destination are in synch:\n")
    dcmp = dircmp(sync_src, sync_dst)
    print_diff_files(dcmp)


'''
Run the test cases
'''
msg_queue = queue.Queue()

printhandler = PrintHandlerThread(msg_queue)
printhandler.start()

test_root_folder = os.path.realpath(".\\test")

run_test_case(test_root=test_root_folder, test_case="TestCase1", model_folder="Model", src="foo", dst="foo1")
run_test_case(test_root=test_root_folder, test_case="TestCase2", model_folder="Model", src="Test1", dst="Test2")
run_test_case(test_root=test_root_folder, test_case="TestCase3", model_folder="Model", src="foo", dst="foo1")
run_test_case(test_root=test_root_folder, test_case="TestCase4", model_folder="Model", src="src", dst="dst")

printhandler.join()
