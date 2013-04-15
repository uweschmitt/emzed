'''Michael Lange <klappnase (at) freakmail (dot) de>
The Meter class provides a simple progress bar widget for Tkinter.

INITIALIZATION OPTIONS:
The widget accepts all options of a Tkinter.Frame plus the following:

    fillcolor -- the color that is used to indicate the progress of the
                 corresponding process; default is "orchid1".
    value -- a float value between 0.0 and 1.0 (corresponding to 0% - 100%)
             that represents the current status of the process; values higher
             than 1.0 (lower than 0.0) are automagically set to 1.0 (0.0); default is 0.0 .
    text -- the text that is displayed inside the widget; if set to None the widget
            displays its value as percentage; if you don't want any text, use text="";
            default is None.
    font -- the font to use for the widget's text; the default is system specific.
    textcolor -- the color to use for the widget's text; default is "black".

WIDGET METHODS:
All methods of a Tkinter.Frame can be used; additionally there are two widget specific methods:

    get() -- returns a tuple of the form (value, text)
    set(value, text) -- updates the widget's value and the displayed text;
                        if value is omitted it defaults to 0.0 , text defaults to None .
'''

import Tkinter
import tkFileDialog
import tkMessageBox
import Queue


class ThreadsafeMeter(Tkinter.Frame):
    def __init__(self, master, width=300, height=20, bg='white',
            fillcolor='lightblue',\
                 value=0.0, text=None, font=None, textcolor='black', *args, **kw):
        Tkinter.Frame.__init__(self, master, bg=bg, width=width, height=height, *args, **kw)
        self._value = value

        self._canv = Tkinter.Canvas(self, bg=self['bg'], width=self['width'], height=self['height'],\
                                    highlightthickness=0, relief='flat', bd=0)
        self._canv.pack(fill='both', expand=1)
        self._rect = self._canv.create_rectangle(0, 0, 0, self._canv.winfo_reqheight(), fill=fillcolor,\
                                                 width=0)
        self._text = self._canv.create_text(self._canv.winfo_reqwidth()/2, self._canv.winfo_reqheight()/2,\
                                            text='', fill=textcolor)
        if font:
            self._canv.itemconfigure(self._text, font=font)

        self.bind('<Configure>', self._update_coords)

        self.queue = Queue.Queue()
        self.running = True
        self.update_me()
        self.set(value, text)

    def _update_coords(self, event):
        '''Updates the position of the text and rectangle inside the canvas when the size of
        the widget gets changed.'''
        # looks like we have to call update_idletasks() twice to make sure
        # to get the results we expect
        self._canv.update_idletasks()
        self._canv.coords(self._text, self._canv.winfo_width()/2, self._canv.winfo_height()/2)
        self._canv.coords(self._rect, 0, 0, self._canv.winfo_width()*self._value, self._canv.winfo_height())
        self._canv.update_idletasks()

    def get(self):
        return self._value, self._canv.itemcget(self._text, 'text')

    def set(self, value=0.0, text=None):
        self.queue.put((value, text))

    def update_me(self):
        try:
            while 1:
                head = self.queue.get_nowait()
                value, text = head
                self._set(value=value, text=text)
                self.update_idletasks()
                self._canv.update_idletasks()
        except Queue.Empty:
            pass
        self.after(200, self.update_me)

    def _set(self, value=0.0, text=None):
        #make the value failsafe:
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        self._value = value
        if text == None:
            #if no text is specified use the default percentage string:
            text = str(int(round(100 * value))) + ' %'
        self._canv.coords(self._rect, 0, 0, self._canv.winfo_width()*value, self._canv.winfo_height())
        self._canv.itemconfigure(self._text, text=text)
        self._canv.update_idletasks()
        self.update_idletasks()


from Tkinter import *
import os
import threading
import random
import time
import urllib2

class Downloader(threading.Thread):

    def __init__(self, url, txt, widget):
        threading.Thread.__init__(self)
        self.url = url
        self.widget = widget
        self.txt = txt
        self.done = False

    def run(self):
        value = 0.0
        self.widget.set(value, "wait for " + self.url)

        handler = urllib2.urlopen(self.url)
        n = int(handler.headers["content-length"])
        content = ""
        while True:
            self.widget.set(1.0 * len(content)/n, "loading " + self.txt)
            data = handler.read(1000)
            if not data:
                break
            content += data
        self.widget.set(1.0, "finished download of " + self.txt)
        self.done = True


class Dialog(object):

    def __init__(self, urls):

        root = Tk(className='meter demo')
        self.root = root

        l = Label(root, text="""
        This is the eMZed download helper.

        Please choose a target directory below for storing the downloaded
        packages, we recommend to create a new empty folder for this.

        To start the downloads pess "GO!".

        You can close the dialog if all downloads are finished. For completing
        the installlation of eMZed open the target folder and run the
        downloaded files in numbered order.
        """).grid(row=0, columnspan=3)

        l = Label(root, text="Target path for downloads:").grid(row=1,
                column=0)

        home = os.environ.get("HOME") or os.environ.get("HOMEPATH")
        self.targetdir = os.path.join(home, "Downloads")
        target = StringVar(value=self.targetdir)
        self.e = Entry(root, textvariable=target)
        self.e.grid(row=1, column=1)
        self.choose = Button(root, text="Choose Directory", command=self.file_dialog)
        self.choose.grid(row=1, column=2, pady=2)

        self.go = Button(root, text="Go!", command=self.download)
        self.go.grid(row=2, column=0, columnspan=3, pady=10, sticky=N+S+E+W)

        self.bars = []
        self.urls = urls
        for i, (url, txt) in enumerate(urls):
            bar = ThreadsafeMeter(root, width=500, value=0, text=txt)
            bar.grid(row=i+3, columnspan=3, pady=2)
            self.bars.append(bar)

        self.done = Button(root, text = "Close Dialog", command=self.quit)
        self.done.grid(row=5, pady = 5, columnspan = 3, sticky=N+S+E+W)
        self.done.config(state=DISABLED)

    def file_dialog(self):
        dirname=tkFileDialog.askdirectory(initialdir=self.targetdir,mustexist=False)
        self.targetdir=dirname
        self.e.delete(0, END)
        self.e.insert(0, dirname)

    def download(self):
        targetdir = self.targetdir
        if not os.path.exists(targetdir):
            try:
                os.makedirs(targetdir)
            except:
                import traceback
                tkMessageBox.showerror(message=traceback.format_exc())
                return

        self.go["state"] = DISABLED
        self.e["state"] = DISABLED
        self.choose["state"] = DISABLED
        self.root.update_idletasks()
        downloaders = []
        for ((url, txt), bar) in zip(self.urls, self.bars):
            d = Downloader(url, txt, bar)
            downloaders.append(d)
        for d in downloaders:
            d.start()

        self.downloaders = downloaders
        self.root.after(200, self.check_finished)

    def check_finished(self):

        if any(d.isAlive() for d in self.downloaders):
            self.root.after(200, self.check_finished)

        else:
            self.go["state"] = NORMAL
            self.e["state"] = NORMAL
            self.choose["state"] = NORMAL
            self.done["state"] = NORMAL
            self.root.update_idletasks()

    def quit(self):
        self.root.quit()



r=Dialog([("http://www.python.org/index.html", "Python 2.7.4"),
          ("http://emzed.ethz.ch/index.html", "pyopenms"),
          ])
r.root.mainloop()
