import tkinter as tk
from tkinter import ttk
from typing import Any


class Picker(ttk.Frame):

    def __init__(self, master=None, activebackground='#b1dcfb', values=None, entry_wid=None, activeforeground='black',
                 selectbackground='#003eff', selectforeground='white', command=None, borderwidth=1, relief="solid",
                 frameheight=120):

        if values is None:
            values = []
        self._selected_item = None
        self._frameheight = frameheight
        self._values = values

        self._entry_wid = entry_wid

        self._sel_bg = selectbackground
        self._sel_fg = selectforeground

        self._act_bg = activebackground
        self._act_fg = activeforeground

        self._command = command
        self.index = 0
        ttk.Frame.__init__(self, master, borderwidth=borderwidth, height=10, relief=relief)

        self.bind("<FocusIn>", lambda event: self.event_generate('<<PickerFocusIn>>'))
        self.bind("<FocusOut>", lambda event: self.event_generate('<<PickerFocusOut>>'))
        f = tk.LabelFrame(self)
        f.pack(fill='x')
        self.canvas = tk.Canvas(f, scrollregion=(0, 0, 500, (len(self._values) * 23 + 3)))
        vbar = tk.Scrollbar(f, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        frame = tk.Frame(self.canvas)
        vbar.config(command=self.canvas.yview)
        self.canvas.create_window((0, 0,), window=frame, anchor='nw', tags='frame')

        self.canvas.config(highlightthickness=0)  # 去掉选中边框
        vbar.config(command=self.canvas.yview)
        self.canvas.config(width=300, height=self._frameheight)
        self.canvas.config(yscrollcommand=vbar.set)
        self.dict_checkbutton = {}
        self.dict_checkbutton_var = {}
        self.dict_intvar_item = {}
        for index, item in enumerate(self._values):
            self.dict_intvar_item[item] = tk.IntVar()
            self.dict_checkbutton[item] = ttk.Checkbutton(frame, text=item, variable=self.dict_intvar_item[item],
                                                          command=lambda ITEM=item: self._command(ITEM))
            self.dict_checkbutton[item].grid(row=index, column=0, sticky=tk.NSEW, padx=5)
            self.dict_intvar_item[item].set(0)
            if item in self._entry_wid.get().split(','):
                self.dict_intvar_item[item].set(1)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas.bind("<MouseWheel>", self.processwheel)
        frame.bind("<MouseWheel>", self.processwheel)
        for i in self.dict_checkbutton:
            self.dict_checkbutton[i].bind("<MouseWheel>", self.processwheel)
        self.bind("<MouseWheel>", self.processwheel)

    def processwheel(self, event):
        a = int(-event.delta)
        if a > 0:
            self.canvas.yview_scroll(1, tk.UNITS)
        else:
            self.canvas.yview_scroll(-1, tk.UNITS)


class Combopicker(ttk.Entry, Picker):
    values: list[Any] | Any

    def __init__(self, master, values=None, entryvar=None, entrywidth=None, entrystyle=None, onselect=None,
                 activebackground='#b1dcfb', activeforeground='black', selectbackground='#003eff',
                 selectforeground='white', borderwidth=1, relief="solid", frameheight=50):
        self.onselect = onselect
        self.relief = relief
        self.borderwidth = borderwidth
        if values is None:
            values = []
        self.values = values
        self.master = master
        self.activeforeground = activeforeground
        self.activebackground = activebackground
        self.selectbackground = selectbackground
        self.selectforeground = selectforeground
        self.frameheight = frameheight
        if entryvar is not None:
            self.entry_var = entryvar
        else:
            self.entry_var = tk.StringVar()
        self.show_var = tk.StringVar()
        entry_config = {}
        if entrywidth is not None:
            entry_config["width"] = entrywidth

        if entrystyle is not None:
            entry_config["style"] = entrystyle

        ttk.Entry.__init__(self, master, textvariable=self.show_var, **entry_config, state="")

        self._is_menuoptions_visible = False

        self.picker_frame = Picker(self.winfo_toplevel(), values=self.values, entry_wid=self.entry_var,
                                   activebackground=activebackground,
                                   activeforeground=activeforeground, selectbackground=selectbackground,
                                   selectforeground=selectforeground, command=self._on_selected_check,
                                   frameheight=self.frameheight)

        self.bind_all("<1>", self._on_click, "+")

        self.bind("<Escape>", lambda event: self.hide_picker())

    @property
    def current_value(self):
        try:

            value = self.entry_var.get()
            return value
        except ValueError:
            return None

    @current_value.setter
    def current_value(self, INDEX):
        self.entry_var.set(self.values.index(INDEX))

    def _on_selected_check(self, SELECTED):
        value = []
        all_name = '全选'

        if self.entry_var.get() != "" and self.entry_var.get() is not None:
            temp_value = self.entry_var.get()
            value = temp_value.split(",")
        if str(SELECTED) in value:
            if all_name == str(SELECTED):
                value.clear()  # 清空选项
            else:
                if all_name in value:
                    value.remove(all_name)
                value.remove(str(SELECTED))
                value.sort()
        else:
            if all_name == str(SELECTED):
                value = self.values
            else:
                value.append(str(SELECTED))
                value.sort()
        temp_value = ""
        for index, item in enumerate(value):
            if item != "":
                if index != 0:
                    temp_value += ","
                temp_value += str(item)
        self.entry_var.set(temp_value)
        if '全选' in self.entry_var.get().split(','):
            self.show_var.set(self.entry_var.get()[3::])
        else:
            self.show_var.set(self.entry_var.get())
        # 全选刷新
        if all_name == str(SELECTED):
            self.hide_picker()
            self.show_picker()

    def _on_click(self, event):
        str_widget = str(event.widget)

        if str_widget == str(self):
            if not self._is_menuoptions_visible:
                self.show_picker()
        else:
            if not str_widget.startswith(str(self.picker_frame)) and self._is_menuoptions_visible:
                self.hide_picker()

    def show_picker(self):

        if not self._is_menuoptions_visible:
            self.picker_frame = Picker(self.winfo_toplevel(), values=self.values, entry_wid=self.entry_var,
                                       frameheight=self.frameheight, activebackground=self.activebackground,
                                       activeforeground=self.activeforeground, selectbackground=self.selectbackground,
                                       selectforeground=self.selectforeground, command=self._on_selected_check)

            self.bind_all("<1>", self._on_click, "+")

            self.bind("<Escape>", lambda event: self.hide_picker())
            self.picker_frame.lift()
            self.picker_frame.place(in_=self, relx=0, rely=1, relwidth=1)
        self._is_menuoptions_visible = True

    def hide_picker(self):
        if self._is_menuoptions_visible:
            self.picker_frame.place_forget()
            # self.picker_frame.destroy()   # mac下直接销毁控件
        self._is_menuoptions_visible = False
