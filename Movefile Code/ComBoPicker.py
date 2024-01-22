import tkinter as tk
from tkinter import ttk


class Picker(ttk.Frame):

    def __init__(self, master=None, activebackground='#b1dcfb', values=None, entry_wid=None, activeforeground='black',
                 selectbackground='#003eff', selectforeground='white', command=None, borderwidth=1, relief=['flat'],
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

        if not command is None:
            self._command = command
        else:
            raise ValueError
        
        if not entry_wid is None:
            self._entry_wid = entry_wid
        else:
            raise ValueError
        
        self.index = 0
        ttk.Frame.__init__(
            self, master, borderwidth=borderwidth, height=10, relief=relief)

        self.bind("<FocusIn>", lambda event: self.event_generate(
            '<<PickerFocusIn>>'))
        self.bind("<FocusOut>", lambda event: self.event_generate(
            '<<PickerFocusOut>>'))
        f = tk.LabelFrame(self)
        f.pack(fill='x')
        self.canvas = tk.Canvas(f, scrollregion=(
            0, 0, 500, (len(self._values) * 23 + 3)))
        vbar = tk.Scrollbar(f, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        frame = tk.Frame(self.canvas)
        vbar.config(command=self.canvas.yview)
        self.canvas.create_window(
            (0, 0,), window=frame, anchor='nw', tags='frame')

        self.canvas.config(highlightthickness=0)  # 去掉选中边框
        vbar.config(command=self.canvas.yview)
        self.canvas.config(width=300, height=self._frameheight)
        self.canvas.config(yscrollcommand=vbar.set)
        self.dict_checkbutton = {}
        self.dict_intvar_item = {}
        for index, item in enumerate(self._values):
            self.dict_intvar_item[item] = tk.IntVar()
            self.dict_checkbutton[item] = ttk.Checkbutton(frame, text=item, variable=self.dict_intvar_item[item],
                                                          command=lambda ITEM=item: self._command(ITEM))
            self.dict_checkbutton[item].grid(
                row=index, column=0, sticky=tk.NSEW, padx=5)
            self.dict_intvar_item[item].set(0)
            if item in self._entry_wid.get().split('|'):
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

    def __init__(self, master, values=None, entryvar=None, entrywidth=None, entrystyle=None, onselect=None,
                 activebackground='#b1dcfb', activeforeground='black', selectbackground='#003eff',
                 selectforeground='white', borderwidth=1, relief="solid", frameheight=50, allname_textvariable=None):
        self.onselect = onselect
        self.relief = relief
        self.borderwidth = borderwidth
        if values is None:
            values = []
        self.values = values
        if not allname_textvariable is None:
            self.allname_var = allname_textvariable
        else:
            raise ValueError
        self.previous_allname = self.allname_var.get()
        self.values.append(self.previous_allname)
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

        ttk.Entry.__init__(
            self, master, textvariable=self.show_var, **entry_config, state="")

        self._is_menuoptions_visible = False

        self.picker_frame = Picker(self.winfo_toplevel(), values=self.values, entry_wid=self.entry_var,
                                   activebackground=activebackground,
                                   activeforeground=activeforeground, selectbackground=selectbackground,
                                   selectforeground=selectforeground, command=self.on_selected_check,
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
        self.entry_var.set(str(self.values.index(INDEX)))

    def change_language(self, label_name):
        self.allname_var.set(label_name)
        self.values[0] = label_name

    def all_selected(self, _values):
        for item in self.values[1:]:
            if not item in _values:
                return False
        return True
    
    def update_values(self, values_in):
        self.values = [self.allname_var.get()] + values_in
        previous_values = self.get().split('|')
        result = ''
        for pre_value in previous_values:
            if pre_value in values_in:
                result += pre_value + '|'
        if not result == '' and result[-1] == '|':
            result = result[:-1]
        self.delete(0, 'end')
        self.insert(0, result)

    def append_value(self, new_value):
        if not new_value in self.values:
            self.values.append(new_value)
            self.update_values(self.values[1:])
        self.on_selected_check(new_value)
        self.hide_picker()
    
    def on_selected_check(self, SELECTED):
        value = []
        all_name = self.allname_var.get()
        need_refresh = False

        if self.entry_var.get() != "" and self.entry_var.get() is not None:
            temp_value = self.entry_var.get()
            value = temp_value.split('|')
        if str(SELECTED) in value:
            if all_name == str(SELECTED):
                value.clear()  # 清空选项
                need_refresh = True
            else:
                if all_name in value:
                    value.remove(all_name)
                    need_refresh = True
                value.remove(str(SELECTED))
                value.sort()
        else:
            if all_name == str(SELECTED):
                value = self.values
                need_refresh = True
            else:
                value.append(str(SELECTED))
                value.sort()
                if self.all_selected(value):
                    value = self.values
                    need_refresh = True
        temp_value = ""
        for index, item in enumerate(value):
            if item != "" and index > 0:
                temp_value += '|'
            temp_value += str(item)
        self.entry_var.set(temp_value)
        if all_name in self.entry_var.get().split('|'):
            self.show_var.set(self.entry_var.get()[len(all_name)+1:])
        else:
            self.show_var.set(self.entry_var.get())
        # 全选刷新
        if need_refresh:
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
        if self.previous_allname != self.allname_var.get():  # Check Select_All label
            self.change_language(self.allname_var.get())
            self.previous_allname = self.allname_var.get()
        if not self._is_menuoptions_visible:
            self.picker_frame = Picker(self.winfo_toplevel(), values=self.values, entry_wid=self.entry_var,
                                       frameheight=self.frameheight, activebackground=self.activebackground,
                                       activeforeground=self.activeforeground, selectbackground=self.selectbackground,
                                       selectforeground=self.selectforeground, command=self.on_selected_check)

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
