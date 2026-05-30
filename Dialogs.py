import tkinter as tk
import pdb
from window import TextMatrix

ASCII = "ascii"
HEX = "hex"

class Dialog:
    def __init__(self, editor, update_window_func = None):
        self.editor = editor
        self.root = editor.root
        self.update_window_func = update_window_func
        
        self.window = tk.Toplevel(self.root)
        self.window.title("Unknown")
        self.window.resizable(False, False)
        self.window.transient(self.root)
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        self.window.withdraw()

        self.search_format = tk.StringVar(value=ASCII)
        self.scope_mode = tk.StringVar(value="cursor")
        self.matchCase_check = tk.BooleanVar(value=False)
        self.wholeWord_check = tk.BooleanVar(value=False)
        self.wrapAround_check = tk.BooleanVar(value=True)

        self.string_ascii = tk.StringVar()
        self.string_hex = tk.StringVar()
        self.replace_hex_string = tk.StringVar()
        self.replace_ascii_string = tk.StringVar()

        self.build_frames()
        self.bind_tab_switch()
        
        self.bind_string_change(self.hex_entry, self.string_hex)
        self.bind_string_change(self.replace_hex_entry, self.replace_hex_string)

        self.replaceMode = False

        self.hex_entry.bind("<ButtonRelease-1>", self.on_key)


    @property
    def dialog_type(self):
        return self.window.title()

    @dialog_type.setter
    def dialog_type(self, value):
        self.window.title(value)

    @property
    def options(self):
        return self.get_search_options()

    def on_key(self, event):
        self.lastChar = event.char
#        pdb.set_trace()
        if event:
            print(vars(event))
            tm = TextMatrix(event)
            tm.vertical_print()
            tm.print(' ')
        else:
            print(f'on_key - event NONE')

        if event.keysym == "Insert" and event.type == tk.EventType.KeyPress:
            self.replaceMode = not self.replaceMode
            self.hex_entry.after_idle(lambda: self.update_entryReplaceSelection(event))
            
        if event:
            if self.replaceMode == True:  
                self.hex_entry.after_idle(lambda: self.update_entryReplaceSelection(event))

    def update_entryReplaceSelection(self, event):
        cursor_pos = self.hex_entry.index(tk.INSERT)
##        txt = self.hex_entry.get()

##        if cursor_pos < len(txt) and txt[cursor_pos] == ' ':
##            if event.keysym == "Right":
##                cursor_pos += 1
##                self.hex_entry.icursor(cursor_pos)
##            if event.keysym == "Left":
##                cursor_pos -= 1
##                self.hex_entry.icursor(cursor_pos)
                
        if self.replaceMode:
##            self.hex_entry.selection_range(cursor_pos, cursor_pos + 1)
##            self.hex_entry.config(selectbackground="red",
##                                  selectforeground="white")
                    self.hex_entry.config(insertwidth=5,
                                          insertbackground="red",
                                          insertborderwidth=1)
        else:
                    self.hex_entry.config(insertwidth=2,
                                          insertbackground="black",
                                          insertborderwidth=0)
##            self.hex_entry.selection_clear()
        return
                       
    def bind_string_change(self, entry: tk.Entry, string_var: tk.StringVar):
        string_var.trace("w", lambda name, index, mode: self.on_string_change(entry, string_var, name, index, mode))

    def on_string_change(self, entry, string_var, name, index, mode):
        print(f'String HEX changed. Name:{name}, index:{index}, mode:{mode}')
        txt = string_var.get()
        cursor_pos = entry.index(tk.INSERT)
        chars_before_cursor = cursor_pos - txt[:cursor_pos].count(' ')

        res = []
        delindex = None

        if self.lastChar in '0123456789ABCDEFabcdef':
            if self.replaceMode and cursor_pos < len(txt):
                delindex = cursor_pos
                if txt[delindex] == ' ':
                    delindex += 1
        else:
            print(f'\n' + 'Invalid HEX symbol was entered: {repr(self.lastChar)}')
            print(f'Supported HEX symbols: 0123456789ABCDEFabcdef' + '\n')

        for i, c in enumerate(txt):
            if c in '0123456789ABCDEFabcdef':
                if i == delindex:
                    continue
                c = c.upper()
                
                if len(res) % 3 == 2:
                    res.append(' ')
                res.append(c)

        new_cursor_pos = chars_before_cursor + ((chars_before_cursor +1) // 2 - 1)

        string_var.set(''.join(res))
        self.window.after_idle(lambda: entry.icursor(new_cursor_pos))
        
        
        
    def bind_tab_switch(self):
        self.window.bind("<Control-Tab>", self.switch_dialog)

    def switch_dialog(self, event=None):
        if self.dialog_type == "SearchDialog":
            self.editor.create_dialog("ReplaceDialog")
        elif self.dialog_type == "ReplaceDialog":
            self.editor.create_dialog("SearchDialog")
        else:
            return
        
    def display(self, switch_mode):
        if switch_mode == "search":
            self.dialog_type = "SearchDialog"
            self.replace_frame.grid_remove()
            self.btn_Replace_FindUp.grid_remove()
            self.btn_Replace_FindDown.grid_remove()
            self.btn_ReplaceAll.grid_remove()
        elif switch_mode == "replace":
            self.dialog_type = "ReplaceDialog"
            self.replace_frame.grid()
            self.btn_Replace_FindUp.grid()
            self.btn_Replace_FindDown.grid()
            self.btn_ReplaceAll.grid()

    def get_search_options(self):
        class Options:
            def __init__(self, dialog):
                self.case  = dialog.matchCase_check
                self.word  = dialog.wholeWord_check
                self.wrap  = dialog.wrapAround_check
                self.scope = dialog.scope_mode
                self.search_format  = dialog.search_format
        return Options(self)

    def build_frames(self):
        self.build_find_frame()
        self.build_options_frame()
        self.build_scope_frame()
        self.build_buttons_or_another_frame()

    def build_find_frame(self):
        find_frame = tk.LabelFrame(self.window, text="Find (Ctrl-Tab to switch mode)", padx=5, pady=5)
        find_frame.grid(row=0, column=0, columnspan=2, sticky="wens", padx=5, pady=5)

        tk.Radiobutton(find_frame, text = "Text string", variable=self.search_format, value=ASCII,
                       command=lambda: self.editor.on_search_format_change(self)
                       ).grid(row=0, column=0, sticky='w', padx=0, pady=0)
        tk.Radiobutton(find_frame, text = "Hex string", variable=self.search_format, value=HEX,
                       command=lambda: self.editor.on_search_format_change(self)
                       ).grid(row=2, column=0, sticky='w', padx=0, pady=0)

        self.textbutton = tk.Button(find_frame, text="Text->Hex",  width=8, height=1,
                  command=lambda: self.editor.text_to_hex(self)
                  )
        self.textbutton.grid(row=0, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        
        self.hexbutton = tk.Button(find_frame, text="Hex->Text", width=8, height=1,
                  command=lambda: self.editor.hex_to_text(self)
                  )
        self.hexbutton.grid(row=2, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        
        self.ascii_entry = tk.Entry(find_frame, textvariable=self.string_ascii, width=50)
        self.ascii_entry.grid(row=1, column=0, columnspan=3, sticky="we", padx=0, pady=0)
        
        self.hex_entry = tk.Entry(find_frame, textvariable=self.string_hex)
        self.hex_entry.grid(row=3, column=0, columnspan=3, sticky="we", padx=0, pady=0)

        self.hex_entry.bind("<KeyPress>", self.on_key)
        self.hex_entry.bind("<KeyRelease>", self.on_key)


    def build_options_frame(self):
        opt_frame = tk.LabelFrame(self.window, text="Options", padx=5, pady=5)
        opt_frame.grid(row=2, column=0, sticky="wens", padx=5, pady=5)

        self.match_case_checkbox = tk.Checkbutton(opt_frame, text="Match case", variable=self.matchCase_check)
        self.match_case_checkbox.grid(row=0, column=1, sticky="w")
        self.whole_word_checkbox = tk.Checkbutton(opt_frame, text="Whole word", variable=self.wholeWord_check)
        self.whole_word_checkbox.grid(row=1, column=1, sticky="w")
        self.wrap_around_checkbox = tk.Checkbutton(opt_frame, text="Wrap around", variable=self.wrapAround_check)
        self.wrap_around_checkbox.grid(row=2, column=1, sticky="w")

    def build_scope_frame(self):
        scope_frame = tk.LabelFrame(self.window, text="Scope from", padx=5, pady=5)
        scope_frame.grid(row=2, column=1, sticky="wens", padx=5, pady=5)
        tk.Radiobutton(scope_frame, text="Cursor", variable=self.scope_mode, value="cursor"
                       ).grid(row=0, column=0, sticky="w")
        tk.Radiobutton(scope_frame, text="Begin", variable=self.scope_mode, value="begin"
                       ).grid(row=1, column=0, sticky="w")

    def build_buttons_or_another_frame(self):
        #Search btns
        buttons_frame = tk.LabelFrame(self.window, text=" ", padx=5, pady=5)
        buttons_frame.grid(row=0, column=2, rowspan=2, sticky='wens', padx=5, pady=5)

        self.btn_close = tk.Button(buttons_frame, text="Close", command=self.hide)
        self.btn_close.grid(row=0, column=2, sticky="we", padx=5, pady=5)
        
        self.btn_FindUp = tk.Button(buttons_frame, text="FindUp", command=lambda: self.editor.next_match("up", self))
        self.btn_FindUp.grid(row=1, column=2, sticky="we", padx=5, pady=5)
        
        self.btn_FindDown = tk.Button(buttons_frame, text="FindDown", command=lambda: self.editor.next_match("down", self))
        self.btn_FindDown.grid(row=2, column=2, sticky="we", padx=5, pady=5)
                
        #add replace widgets
        self.replace_frame = tk.LabelFrame(self.window, text="Replace with", padx=5, pady=5)
        self.replace_frame.grid(row=1, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        tk.Label(self.replace_frame, text="Text string:", anchor="w").grid(row=0, column=0, sticky="w", padx=0, pady=(5, 0))
        self.replace_ascii_entry = tk.Entry(self.replace_frame, textvariable=self.replace_ascii_string, width=50)
        self.replace_ascii_entry.grid(row=1, column=0, sticky="we", padx=0, pady=5)

        tk.Label(self.replace_frame, text="Hex string:", anchor="w").grid(row=2, column=0, sticky="w", padx=0, pady=(5, 0))
        self.replace_hex_entry = tk.Entry(self.replace_frame, textvariable=self.replace_hex_string, width=50)
        self.replace_hex_entry.grid(row=3, column=0, sticky="we", padx=0, pady=5)

        #Replace btns
        self.btn_Replace_FindUp = tk.Button(buttons_frame, text="Replace+FindUp", command=lambda: self.editor.replace_next("up", self))
        self.btn_Replace_FindUp.grid(row=3, column=2, sticky="we", padx=5, pady=5)
        
        self.btn_Replace_FindDown = tk.Button(buttons_frame, text="Replace+FindDown", command=lambda: self.editor.replace_next("down", self))
        self.btn_Replace_FindDown.grid(row=4, column=2, sticky="we", padx=5, pady=5)

        #Replace + ALL
        self.btn_ReplaceAll = tk.Button(buttons_frame, text="ReplaceAll", command=lambda: self.editor.replace_all(self))
        self.btn_ReplaceAll.grid(row=5, column=2, sticky="we", padx=5, pady=5)
        
    def hide(self):
        self.window.grab_release()
        self.window.withdraw()

    def show(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_set()
        self.window.grab_set()
