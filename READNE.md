

# Synchdir #

A program to recursively synchronize the files between two directory trees. It was written in Python 3.7 on Windows 10. It has not tested on Mac or Linux.

I have 50 years IT experience with C++, C#, Java, JavaScript. I have recently learned Python and I wanted to write something that I had previously written in C++. I also wanted to apply what I learned to what I considered was a tough problem to solve. 


Directory synchronization means to take two directory trees and make identical. A good use case would be for backups.

Why not just delete the target directory and copy over the source directory? In cases where a directory is backed up often, the two trees would be close to being in synch anyway, so you only want to check the *differences* and bring them into alignment. What makes this program unique and complex is that it does more than just copy files. It detects deleted and moved files.

The program consists of the following modules:

## synchdir.py ##

This module contains all the code necessary to synch two directory trees. It may be run in the following ways:

-  As a standalone module with two arguments: source directory and destination (target) directory
-  Invoked from a UI module, as explained below.
-  Invoked from a test harness, as explained below.

Some synch programs offer various options such as recursive/non-recursive, synchronization in 1 or 2 directions, comparison using file size/date/contents. I decided to stick with the most useful default that is most useful to me: one-way synchronization making the destination directory a mirror copy or the source directory.

If you want to use other synchronization rules, this program is fairly modular and easy to change in the `synchdir` method. The `Synch` class contains the basic logic to copy, delete, and move. It should be applicable to any synchronization logic.

After the synchronization, the destination is an exact image of the source directory, and the source directory is unchanged from the original.

### Logic ###

While a simpler copy-only program would work both directory trees and synchronize along the way, This program needs to know about **ALL** the files in both directories before taking any action in order to detect moved or deleted files. The `synchdir` function begins by walking both trees, collecting information about the files and storing into a large dictionary called `files`, indexed by the file name, with the corresponding item containing separate `src` and `dst` trees indexed by all occurrences of that file in the entire tree.  

`srcdir` contains the name of root source folder  
`dstdir` contains the name of root destination folder
`relpath` contains the path of the file relative to either the `src` or `dst` folder
`file_info` is a class which contains information about a file: modified date, size, src, and a flag indicating whether on not the file has been `visited`.

In the `synchdir` method, when the information is collected, it is stored as follows:

	files[filename].src[relpath] = file_info(size, date)
	files[filename].dst[relpath] = file_info(size, date)

Then we go through the big loop in the program

	# For each file, perform the synchronization by matching the keys
	for key, item in files.items():
    
`key` refers to each file name in `files`, and `item` refers to all instances of the file name in both the source and destination trees. So, synchronization takes place, not folder by folder, but file by file. 

We determine the set of path names common to both folders, source folder only, or destination folder only. This is accomplished by the following code:

	s1 = set(item.src.keys())
	s2 = set(item.dst.keys())
	keysSrcDst = s1.intersection(s2)
	keysSrc = s1.difference(s2)
	keysDst = s2.difference(s1)

Then we loop through each set of keys to perform one of the following operations, as appropriate:

- Ignore a file if it is already in synch
- Copy by overwriting a file in place from source to destination
- Copy a new file from source to destination
- Delete a file in the destination folder that does not exist in the source folder
- Move a file from one place to another in the destination folder to match its location in the source folder


### Logging ###

I am not using logging, but decided to put custom progress messages in a message queue.

Why not logging? I originally used a log, but I wanted to provide a color-coded progress log of progress messages in a ScrolledText window. (See `synchdirUI.py` below). I am not experienced enough to create custom logging levels. In fact, now that the program is complete, I just discovered that custom logging levels even existed. So, I opted for plain messages that could be directed to a UI widget, or printed to `stdout`, or anyplace else your Python imagination takes you. The module `synchdirUI` logs to a widget. The modules `synchdir` and `test_driver.py' log to `stdout`.

## synchdirUI.py ##

I wanted to wrap the synch module in some UI so I could use common dialogs to select the source and destination folders. I also wanted to capture message from `synchdir` and display them in a text window.

I want to acknowledge the following website https://github.com/beenje/tkinter-logging-text-widget for showing how you could log to a TKinter text widget. I began with their code and modified it considerably, adding more controls, more logging levels, and substituting a tuple (operation type, message) and a queue in place of a log record and a logging class.

There are 4 operations that I log in the ScrolledText widget:

- <span style="color:blue">COPYOVER:</span> overwrite a file that exists in the same folder on both source and destination.
- <span style="color:green">COPYNEW:</span> Copy a new file from a source folder that didn't exist anywhere in the  destination tree.
- <span style="color:red">DELETE:</span> Delete a file that exists in the destination directory, but not the source directory.
- <span style="color:magenta">MOVE:</span> Rather than copy and move, detect files that exist in both source and destination, but have been moved. Move the destination file to a location which corresponds to the source.


I commented out some code that lets you generate and display custom as well as standard logging messages, if you want to see how this works.


## test_driver.py ##

I also wrote a test driver script and some test cases. In this project there is a `test` sub-folder which contains a number of test cases. Each test case consists of a "model" folder which contains the actual test case and the expected result. The function `run_test_case` runs each test case using the following logic, and logs its results to `stdout`:

- Ensure the 'model' folder exists.
- If the 'test' folder exists, delete it and recreate it using the 'model' folder, Under the 'model' folder will be two folders: the source folder and the destination folder
- All testing takes place in the 'test' folder.
- Run `synchdir` to synchronize test/source to test/destination
- Compare test/source with test/destination to make sure we synchronized the source with the destination. Use the Python module `from filecmp import dircmp` to verify folder equality
- Compare model/source with test/source to ensure the source directory is unchanged
- The test passes if but the above comparisons find zero differences
	

