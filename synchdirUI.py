import queue
import signal
import threading
from tkinter import StringVar
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, VERTICAL, HORIZONTAL, N, S, E, W
from tkinter import filedialog
import synchdir


defaultSrc = "E:\\F_Drive\\projects\\foo"
defaultDst = "E:\\F_Drive\\projects\\foo1"

msg_queue = queue.Queue()


class SynchDirThread(threading.Thread):
    ''' Call synchdir in the synchdir module in a separate worker thread
    Report actions back to UI module via a queue '''

    def __init__(self, msg_queue):
        super().__init__()
        self._stop_event = threading.Event()
        self.msg_queue = msg_queue

        # Define member variables and set default values
        self.src = defaultSrc
        self.dst = defaultDst

    def run(self):
        msg_queue.put(('INFO', 'Dirsynch started'))
        synchdir.synchdir(msg_queue, self.src, self.dst)

    def stop(self):
        msg_queue.put(('INFO', 'Dirsynch stopped'))
        self._stop_event.set()


class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""

    def __init__(self, frame):
        self.frame = frame

        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(frame, state='disabled', height=12)
        self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        self.scrolled_text.tag_config('COPYOVER', foreground='blue',)
        self.scrolled_text.tag_config('COPYNEW', foreground='green',)
        self.scrolled_text.tag_config('DELETE', foreground='red',)
        self.scrolled_text.tag_config('MOVE', foreground='magenta',)

        # Start polling messages from the queue
        self.frame.after(100, self.poll_log_queue)

    def display(self, record):
        msg = record
        # Send special message to clear the log
        if msg == "__clear__":
            self.scrolled_text.configure(state='normal')
            self.scrolled_text.delete(1.0, tk.END)
            self.scrolled_text.configure(state='disabled')
            return

        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg[1] + '\n', msg[0])
        self.scrolled_text.configure(state='disabled')

        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = msg_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)


class FormUi:
    ''' Main UI form'''

    def __init__(self, frame):
        self.frame = frame

        '''Create a combo box to select the logging level. 
        Attach the logging level to messages and add them to the message queue '''
        # values = ['INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL', 'COPYNEW', 'COPYOVER', 'DELETE', 'MOVE']
        # self.level = tk.StringVar()
        # ttk.Label(self.frame, text='Level:').grid(column=0, row=0, sticky=W)
        # self.combobox = ttk.Combobox(
        #     self.frame,
        #     textvariable=self.level,
        #     width=25,
        #     state='readonly',
        #     values=values
        # )
        # self.combobox.current(0)
        # self.combobox.grid(column=1, row=0, sticky=(W, E))

        # # Create a text field to enter a message
        # self.message = tk.StringVar()
        # ttk.Label(self.frame, text='Message:').grid(column=0, row=1, sticky=W)
        # ttk.Entry(self.frame, textvariable=self.message, width=25).grid(column=1, row=1, sticky=(W, E))

        # # Add a button to log the message
        # self.button = ttk.Button(self.frame, text='Submit', command=self.submit_message)
        # self.button.grid(column=1, row=2, sticky=W)

        # Source and destination folders. Set defaults
        self.strSrc = StringVar()
        self.strDst = StringVar()
        self.strSrc.set(defaultSrc)
        self.strDst.set(defaultDst)

        # Add buttons to browse for folders
        self.button1 = ttk.Button(self.frame, text="Browse for source folder")
        self.button2 = ttk.Button(self.frame, text="Browse for target folder")
        self.button3 = ttk.Button(self.frame, text="Go")
        self.button4 = ttk.Button(self.frame, text="Clear the  Console")

        self.button1.bind("<Button-1>", self.browseSrcFolder)
        self.button2.bind("<Button-1>", self.browseDstFolder)
        self.button3.bind("<Button-1>", self.doSynchDir)
        self.button4.bind("<Button-1>", self.clearConsole)

        self.button1.grid(column=0, row=3, sticky=W)
        self.button2.grid(column=0, row=4, sticky=W)
        self.button3.grid(column=1, row=5, sticky=W)
        self.button4.grid(column=1, row=6, sticky=W)

        # Entries to save the result
        self.entry1 = ttk.Entry(self.frame, textvariable=self.strSrc)
        self.entry2 = ttk.Entry(self.frame, textvariable=self.strDst,)
        self.entry1.config(width=50)
        self.entry2.config(width=50)
        self.entry1.grid(column=1, row=3, sticky=(W, E))
        self.entry2.grid(column=1, row=4, sticky=(W, E))

    def submit_message(self):
        lvl = self.level.get()
        msg_queue.put((lvl, self.message.get()))

    def doSynchDir(self, event):
        global synchDirThread
        synchDirThread.stop()

        # We have to recreate this thread class because threads can only be started once
        synchDirThread = SynchDirThread(msg_queue)
        synchDirThread.src = self.strSrc.get()
        synchDirThread.dst = self.strDst.get()
        msg_queue.put(('INFO', f"doSynchDir: {self.strSrc.get()} {self.strDst.get()}"))
        synchDirThread.start()

    def clearConsole(self, event):
        msg_queue.put("__clear__")

    def browseSrcFolder(self, event):
        dirname = filedialog.askdirectory(parent=self.frame, initialdir="E:/F_drive/Projects", title='Please select a source directory')
        if len(dirname) > 0:
            self.strSrc.set(dirname)

    def browseDstFolder(self, event):
        dirname = filedialog.askdirectory(parent=self.frame, initialdir="E:/F_drive/Projects", title='Please select a destination directory')
        if len(dirname) > 0:
            self.strDst.set(dirname)


class App:

    def __init__(self, root):
        self.root = root
        root.title('SynchDir')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        ''' Create the panes and frames
            vertical_pane
                horizontal_pane
                    form_frame
                    console_frame
        '''
        vertical_pane = ttk.PanedWindow(self.root, orient=VERTICAL)
        vertical_pane.grid(row=0, column=0, sticky="nsew")
        horizontal_pane = ttk.PanedWindow(vertical_pane, orient=HORIZONTAL)
        vertical_pane.add(horizontal_pane)

        form_frame = ttk.Labelframe(horizontal_pane, text="Folders to Synch")
        form_frame.columnconfigure(1, weight=1)
        horizontal_pane.add(form_frame, weight=1)

        console_frame = ttk.Labelframe(horizontal_pane, text="Result")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        horizontal_pane.add(console_frame, weight=1)

        # Initialize all frames. Attach their underlying class.
        self.form = FormUi(form_frame)
        self.console = ConsoleUi(console_frame)

        # Define the worker thread
        global synchDirThread
        synchDirThread = SynchDirThread(msg_queue)

        self.root.protocol('WM_DELETE_WINDOW', self.quit)
        self.root.bind('<Control-q>', self.quit)
        signal.signal(signal.SIGINT, self.quit)

    def quit(self, *args):
        global synchDirThread
        synchDirThread.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    app.root.mainloop()


if __name__ == '__main__':
    main()
