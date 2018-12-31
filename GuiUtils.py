import queue
import threading
import tkinter as tk
import traceback

from Utils import data_path, is_bundled

def set_icon(window):
    er16 = tk.PhotoImage(file=data_path('ER16.gif'))
    er32 = tk.PhotoImage(file=data_path('ER32.gif'))
    er48 = tk.PhotoImage(file=data_path('ER48.gif'))
    window.tk.call('wm', 'iconphoto', window._w, er16, er32, er48) # pylint: disable=protected-access


# Although tkinter is intended to be thread safe, there are many reports of issues
# some which may be platform specific, or depend on if the TCL library was compiled without
# multithreading support. Therefore I will assume it is not thread safe to avoid any possible problems
class BackgroundTask(object):
    def __init__(self, window, code_to_run, *code_arg):
        self.window = window
        self.status = None
        self.queue = queue.Queue()
        self.running = True
        self.task = threading.Thread(target=self.try_run, args=(code_to_run, *code_arg))
        self.task.start()
        self.process_queue()

    def try_run(self, code_to_run, *code_arg):
        try:
            code_to_run(*code_arg)
        except Exception as e:
            self.update_status('Error: ' + str(e))
            if not is_bundled():
                traceback.print_exc()
        self.queue_event(self.stop)

    def update_status(self, text):
        self.status = text

    def stop(self):
        self.running = False

    #safe to call from worker
    def queue_event(self, event):
        self.queue.put(event)

    def process_queue(self):
        try:
            while True:
                if not self.running:
                    return
                event = self.queue.get_nowait()
                event()
                if self.running:
                    #if self is no longer running self.window may no longer be valid
                    self.window.update_idletasks()
        except queue.Empty:
            pass
        if self.running:
            self.window.after(100, self.process_queue)


class BackgroundTaskProgress(BackgroundTask):
    def __init__(self, parent, title, code_to_run, *code_arg):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window['padx'] = 5
        self.window['pady'] = 5

        try:
            self.window.attributes("-toolwindow", 1)
        except tk.TclError:
            pass

        self.window.title(title)

        self.lastpercent = 0
        self.progress_var = tk.DoubleVar()
        self.progress = tk.ttk.Progressbar(self.window, variable=self.progress_var, length=300)
        self.progress.pack()

        self.label_var = tk.StringVar(value="")
        self.label = tk.Label(self.window, textvariable=self.label_var, width=50, wrap=300)
        self.label.pack()

        self.button_var = tk.StringVar(value="Please wait...")
        self.button = tk.Button(self.window, textvariable=self.button_var, width=10, height=2, state='disabled', command=self.close)
        self.button.pack()

        self.window.resizable(width=False, height=False)
        set_icon(self.window)

        self.window.transient(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.close_pass)
        self.window.grab_set()
        self.window.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+150))
        self.window.focus_set()

        super().__init__(self.window, code_to_run, *tuple(list(code_arg) + [self]))

        self.parent.wait_window(self.window)

    def close_pass(self):
        pass

    #safe to call from worker thread
    def update_status(self, text):
        self.queue_event(lambda: self.label_var.set(text))

    def update_progress(self, val):
        if int(val) != self.lastpercent:
            self.lastpercent = int(val)
            self.queue_event(lambda: self.progress_var.set(val))

    def update_title(self, text):
        self.queue_event(lambda: self.window.title(text))

    def close(self):
        self.running = False
        self.window.destroy()

    def stop(self):
        self.running = False
        self.progress_var.set(100)
        self.window.bell()
        self.button.configure(state='normal')
        self.button_var.set("OK")


class Dialog(tk.Toplevel):
    def __init__(self, parent, title=None, question=None, oktext=None, canceltext=None):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = False

        if question:
            body = tk.Frame(self)
            label = tk.Label(body, text=question, width=50, wrap=200)
            label.pack()
            body.pack(padx=5, pady=5)

        box = tk.Frame(self)

        w = tk.Button(box, text=oktext if oktext else "OK", width=20, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text=canceltext if canceltext else "Cancel", width=20, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+150))

        self.wait_window(self)

    #
    # standard button semantics
    def ok(self, event=None):
        self.result = True
        self.withdraw()
        self.update_idletasks()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()


class ToolTips(object):
    # This class derived from wckToolTips which is available under the following license:

    # Copyright (c) 1998-2007 by Secret Labs AB
    # Copyright (c) 1998-2007 by Fredrik Lundh
    #
    # By obtaining, using, and/or copying this software and/or its
    # associated documentation, you agree that you have read, understood,
    # and will comply with the following terms and conditions:
    #
    # Permission to use, copy, modify, and distribute this software and its
    # associated documentation for any purpose and without fee is hereby
    # granted, provided that the above copyright notice appears in all
    # copies, and that both that copyright notice and this permission notice
    # appear in supporting documentation, and that the name of Secret Labs
    # AB or the author not be used in advertising or publicity pertaining to
    # distribution of the software without specific, written prior
    # permission.
    #
    # SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO
    # THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
    # FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR
    # ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    # WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    # ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
    # OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

    label = None
    window = None
    active = 0
    tag = None
    after_id = None

    @classmethod
    def getcontroller(cls, widget):
        if cls.tag is None:

            cls.tag = "ui_tooltip_%d" % id(cls)
            widget.bind_class(cls.tag, "<Enter>", cls.enter)
            widget.bind_class(cls.tag, "<Leave>", cls.leave)
            widget.bind_class(cls.tag, "<Motion>", cls.motion)
            widget.bind_class(cls.tag, "<Destroy>", cls.leave)

            # pick suitable colors for tooltips
            try:
                cls.bg = "systeminfobackground"
                cls.fg = "systeminfotext"
                widget.winfo_rgb(cls.fg)  # make sure system colors exist
                widget.winfo_rgb(cls.bg)
            except Exception:
                cls.bg = "#ffffe0"
                cls.fg = "black"

        return cls.tag

    @classmethod
    def register(cls, widget, text):
        if isinstance(text, str):
            text = '\n'.join([line.strip() for line in text.splitlines()]).strip()
        widget.ui_tooltip_text = text
        widget.ui_tooltip_text_prev = None
        tags = list(widget.bindtags())
        tags.append(cls.getcontroller(widget))
        widget.bindtags(tuple(tags))

    @classmethod
    def unregister(cls, widget):
        tags = list(widget.bindtags())
        tags.remove(cls.getcontroller(widget))
        widget.bindtags(tuple(tags))

    # event handlers
    @classmethod
    def enter(cls, event):
        widget = event.widget
        if not cls.label:
            # create and hide balloon help window
            cls.popup = tk.Toplevel(bg=cls.fg, bd=1)
            cls.popup.overrideredirect(1)
            cls.popup.withdraw()
            cls.label = tk.Label(
                cls.popup, fg=cls.fg, bg=cls.bg, bd=0, padx=2, justify=tk.LEFT, wrap=400
            )
            cls.label.pack()
        cls.active = 1
        cls.xy = event.x_root + 16, event.y_root + 10
        cls.event_xy = event.x, event.y
        cls.after_id = widget.after(200, cls.display, widget)

    @classmethod
    def motion(cls, event):
        cls.xy = event.x_root + 16, event.y_root + 10
        cls.event_xy = event.x, event.y
        cls.display(event.widget)

    @classmethod
    def display(cls, widget):
        # display balloon help window
        if cls.active:
            text = widget.ui_tooltip_text
            if callable(text):
                text = text(widget, cls.event_xy)
                if not text:
                    return
            if widget.ui_tooltip_text_prev == text:
                return
                
            widget.ui_tooltip_text_prev = text
            cls.label.config(text=text)
            cls.popup.deiconify()
            cls.popup.lift()
            cls.popup.geometry("+%d+%d" % cls.xy)
            cls.after_id = None

    @classmethod
    def leave(cls, event):
        widget = event.widget
        widget.ui_tooltip_text_prev = None
        if cls.active:
            cls.popup.withdraw()
            cls.active = 0
        if cls.after_id:
            widget.after_cancel(cls.after_id)
            cls.after_id = None


class ValidatingEntry(tk.Entry):
    def __init__(self, master, command=lambda:True, validate=lambda self, value: value, **kw):
        tk.Entry.__init__(self, master, **kw)
        self.validate = validate
        self.command = command

        if 'textvariable' in kw:
            self.__variable = kw['textvariable']
        else:
            self.__variable = tk.StringVar()
        self.__prev_value = self.__variable.get()

        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def __callback(self, *dummy):
        new_value = self.__variable.get()
        valid_value = self.validate(new_value)
        if valid_value is None:
            self.__variable.set(self.__prev_value)
        elif valid_value != new_value:
            self.__prev_value = valid_value
            self.__variable.set(self.valid_value)
        else:
            self.__prev_value = new_value
        self.command()


class SearchBox(tk.ttk.Combobox):
    def __init__(self, master, options, **kw):
        tk.ttk.Combobox.__init__(self, master, **kw)
        self.options = options

        if 'textvariable' in kw:
            self.__variable = kw['textvariable']
        else:
            self.__variable = tk.StringVar()

        self.__variable.trace('w', self.__callback)
        self.bind("<<ComboboxSelected>>", self.__select_callback)

        self.config(textvariable=self.__variable, values=list(self.options))

    def __callback(self, *dummy):
        search_key = self.__variable.get().lower()

        filter_options = list(filter(lambda value: search_key in value.lower(), self.options))
        self.config(values=filter_options)

    def __select_callback(self, *dummy):
        self.config(values=list(self.options))

