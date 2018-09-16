import os
import sys
import time
from stat import *
import stat
import math
import zlib
import queue
import shutil
import threading
import PySimpleGUI as sg
from subprocess import check_output, CalledProcessError



class file_pair:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def __repr__(self):
        return repr((repr(self.src), repr(self.dst)))


class file_info:
    def __init__(self, size, date):
        self.file_size = size
        self.file_date = date
        self.visited = False
        self.crc = 0

    def __repr__(self):
        file_size = convert_size(self.file_size)
        return repr((file_size, time.asctime(time.localtime(self.file_date)), self.visited, self.crc))

    def __eq__(self, other):
        return (self.file_size, self.file_date) == (other.file_size, other.file_date)

    def __gt__(self, other):
        return (self.file_size, self.file_date) > (other.file_size, other.file_date)


class Synch:
    def __init__(self, src, dst, msg_queue):
        self.src = src
        self.dst = dst
        self.msg_queue = msg_queue

    def copy(self, relpath, filename, msg):
        srcpath = os.path.join(self.src, relpath, filename)
        dstpath = os.path.join(self.dst, relpath, filename)
        dest_folder = os.path.dirname(dstpath)

        self.msg_queue.put((msg, f"{srcpath} to {dstpath}"))

        # Destination path must already exist
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
            
        # If hidden file
        was_hidden = False
        if self.has_hidden_attribute(srcpath):
            was_hidden = True
            self.show_file(srcpath)
            self.show_file(dstpath)
        
        try:
            shutil.copy2(srcpath, dstpath)
        except FileNotFoundError as e:
            self.msg_queue.put(('FileNotFoundError', e))
        # This gets files when we try and copy descript.ion files
        except PermissionError as e:
            self.msg_queue.put(('PermissionError', e))
            
        # If was hidden file
        #if was_hidden == True:
            #self.hide_file(srcpath)
            #self.hide_file(dstpath)

    def copy_over(self, relpath, filename):
        self.copy(relpath, filename, 'COPYOVER')

    def copy_new(self, relpath, filename):
        self.copy(relpath, filename, 'COPYNEW')

    def move(self, oldrelpath, newrelpath, filename):
        srcpath = os.path.join(self.dst, oldrelpath, filename)
        dstpath = os.path.join(self.dst, newrelpath, filename)
        old_src_folder = os.path.dirname(srcpath)
        new_dest_folder = os.path.dirname(dstpath)

        self.msg_queue.put(('MOVE', f"{srcpath} to {dstpath}"))

        # destination path must already exist
        if not os.path.exists(new_dest_folder):
            os.makedirs(new_dest_folder)

        try:
            shutil.move(srcpath, dstpath)
        except FileNotFoundError as e:
            self.msg_queue.put(('ERROR', e))
        else:
            self.delete_if_folder_empty(old_src_folder)

    def delete(self, relpath, filename):
        dstpath = os.path.join(self.dst, relpath, filename)
        dest_folder = os.path.dirname(dstpath)

        self.msg_queue.put(('DELETE', f"{dstpath}"))

        try:
            os.remove(dstpath)
        except FileNotFoundError as e:
            self.msg_queue.put(('ERROR', e))
        else:
            self.delete_if_folder_empty(dest_folder)

    def delete_if_folder_empty(self, foldername):
        if not os.listdir(foldername):
            os.rmdir(foldername)
            
    def has_hidden_attribute(self, filepath):
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)    
            
    def hide_file(self, filepath):
        if os.path.exists(filepath):
            self.msg_queue.put(('HIDE', filepath))
            hide_cmd = f'attrib +h {filepath}'
            check_output(hide_cmd, shell = True)
    
    def show_file(self, filepath):
        if os.path.exists(filepath):
            self.msg_queue.put(('SHOW', filepath))
            show_cmd = f'attrib -h {filepath}'
            check_output(show_cmd, shell = True)
    
"""
file_name = 'D:\\Backup\\e\\news\\descript.ion'

dir_cmd = f'dir /b {file_name}'
    
dir_result = check_output(dir_cmd, shell = True).decode()
print('dir', dir_result)

try:
    dir_result = check_output(dir_cmd, shell = True).decode()
    print('dir\n', dir_result)
except CalledProcessError as e:
    pass

"""
            


def convert_size(size_bytes):
    # Used if we want to print file_info
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def crc(fullpath):
    prev = 0
    for eachLine in open(fullpath, "rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X" % (prev & 0xFFFFFFFF)


def get_files_info(rootfolder):
    for root, _, files in os.walk(rootfolder):
        for filename in files:
            # We need the file base name and relative path for use as  keys
            filepath = os.path.join(root, filename)
            relpath = root[len(rootfolder) + 1:]
            st = os.stat(filepath)
            yield (filename, relpath, st[ST_SIZE], st[ST_MTIME])


def synchdir(msg_queue, srcdir, dstdir):
    # Main  function to synchronize folders

    srcdir = os.path.normpath(srcdir)
    dstdir = os.path.normpath(dstdir)

    synch = Synch(srcdir, dstdir, msg_queue)

    # Collect, store and organize the data
    # 'files' is the root dictionary where we store everything
    # The keys 'filename' and 'relpath' are used for classifying and matching
    files = {}

    for filename, relpath, size, date in get_files_info(srcdir):
        if filename not in files:
            src = {}
            dst = {}
            files[filename] = file_pair(src, dst)
        files[filename].src[relpath] = file_info(size, date)

    for filename, relpath, size, date in get_files_info(dstdir):
        if filename not in files:
            src = {}
            dst = {}
            files[filename] = file_pair(src, dst)
        files[filename].dst[relpath] = file_info(size, date)

    # For each file, perform the synchronization by matching the keys
    for key, item in files.items():
        s1 = set(item.src.keys())
        s2 = set(item.dst.keys())

        # These sets identify the files which occur in both folders, or only one of the folders
        keysSrcDst = s1.intersection(s2)
        keysSrc = s1.difference(s2)
        keysDst = s2.difference(s1)

        # Match files that occur in both Source and Destination
        for key1 in keysSrcDst:
            if item.src[key1] == item.dst[key1]:
                # Files are equal -- skip
                item.src[key1].visited = item.dst[key1].visited = True
            else:
                # Files differ in size and/or date -- assume mirror copy from src to dst
                synch.copy_over(key1, key)
                item.src[key1].visited = item.dst[key1].visited = True

        # Get CRC's for remaining files, so we can tell if a file is the same, but has been moved
        # This is expensive, so don't get them until we have to, and when we have to, do so automatically
        for key1 in keysSrc:
            if item.src[key1].visited is False:
                item.src[key1].crc = crc(os.path.join(srcdir, key1, key))

        for key2 in keysDst:
            if item.dst[key2].visited is False:
                item.dst[key2].crc = crc(os.path.join(dstdir, key2, key))

        # If two files are found with matching crc, the file has been moved
        for key1 in keysSrc:
            for key2 in keysDst:
                if item.src[key1].visited is False and item.dst[key2].visited is False:
                    if item.src[key1].crc == item.dst[key2].crc:
                        # File was moved - move (presumes mirror)
                        synch.move(key2, key1, key)
                        item.src[key1].visited = item.dst[key2].visited = True

        # For any orphans left in src: just copy them
        for key1 in keysSrc:
            if item.src[key1].visited is False:
                synch.copy_new(key1, key)
                item.src[key1].visited = True

        # For any orphans left in dst: just delete them
        for key2 in keysDst:
            if item.dst[key2].visited is False:
                synch.delete(key2, key)
                item.dst[key2].visited = True


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
                if record[0] == 'DONE':
                    sg.Popup(record)
                else:
                    sg.Print(record)
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self._stop_event.set()
        super(PrintHandlerThread, self).join(timeout)


def main(argv, defaultSrc, defaultDst):
    try:
        srcdir = argv[1]
        dstdir = argv[2]
    except(IndexError):
        srcdir = defaultSrc
        dstdir = defaultDst

    # If we want to run this module alone without any UI, create a token queue
    msg_queue = queue.Queue()

    printhandler = PrintHandlerThread(msg_queue)
    printhandler.start()
    msg_queue.put(('INFO', "Source directory:", srcdir))
    msg_queue.put(('INFO', "Destination directory:", dstdir))

    synchdir(msg_queue, srcdir, dstdir)
    msg_queue.put(('DONE - Autoclose in 15 sec.'))
    time.sleep(15)
    printhandler.join()


if __name__ == "__main__":
    # Edit these defaults if you want to run without any command-line args
    defaultSrc = "E:\\F_Drive\\projects\\foo"
    defaultDst = "E:\\F_Drive\\projects\\foo1"
    main(sys.argv, defaultSrc, defaultDst)
