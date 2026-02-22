import tkinter as tk

ASCII = "ascii"
HEX = "hex"

class Dialog:
    def __init__(self, editor, dialog_type):
        self.editor = editor
        self.root = self.editor.root
    
        self.window = tk.Toplevel(self.root)
        self.window.title(dialog_type)
        self.window.resizable(False, False)
        self.window.transient(self.root)
        self.window.withdraw()

        self.search_format = tk.StringVar(value=ASCII)
        self.scope_mode = tk.StringVar(value="cursor")
        self.matchCase_check = tk.BooleanVar(value=False)
        self.wholeWord_check = tk.BooleanVar(value=False)
        self.wrapAround_check = tk.BooleanVar(value=True)
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

        self.string_ascii = tk.StringVar()
        self.string_hex = tk.StringVar()

        self.build_frames()
        

    @property
    def dialog_type(self):
        return self.window.title()

    @property
    def options(self):
        return self.get_search_options()

    def get_search_options(self):
        class Options:
            def __init__(self, dialog):
                self.case = dialog.matchCase_check
                self.word = dialog.wholeWord_check
                self.wrap = dialog.wrapAround_check
                self.scope = dialog.scope_mode
                self.format = dialog.search_format
        return Options(self)

    def build_frames(self):
        self.build_find_frame()
        self.build_options_frame()
        self.build_scope_frame()
        self.build_buttons_frame()

    def build_find_frame(self):
        find_frame = tk.LabelFrame(self.window, text="Find", padx=5, pady=5)
        find_frame.grid(row=0, column=0, columnspan=2, sticky="wens", padx=5, pady=5)

        tk.Radiobutton(find_frame, text = "Text string", variable=self.search_format, value=ASCII,
                       command= lambda: self.editor.on_mode_change(self)
                       ).grid(row=0, column=0, sticky='w', padx=0, pady=0)
        tk.Radiobutton(find_frame, text = "Hex string", variable=self.search_format, value=HEX,
                       command= lambda: self.editor.on_mode_change(self)
                       ).grid(row=2, column=0, sticky='w', padx=0, pady=0)


        tk.Button(find_frame, text="Text->Hex",  width=8, height=1,
                  command= lambda: self.editor.text_to_hex(self)
                  ).grid(row=0, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        tk.Button(find_frame, text="Hex->Text", width=8, height=1,
                  command= lambda: self.editor.hex_to_text(self)
                  ).grid(row=2, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        
        self.ascii_entry = tk.Entry(find_frame, textvariable=self.string_ascii, width=50)
        self.ascii_entry.grid(row=1, column=0, columnspan=3, sticky="we", padx=0, pady=0)
        
        self.hex_entry = tk.Entry(find_frame, textvariable=self.string_hex)
        self.hex_entry.grid(row=3, column=0, columnspan=3, sticky="we", padx=0, pady=0)

    def build_options_frame(self):
        opt_frame = tk.LabelFrame(self.window, text="Options", padx=5, pady=5)
        opt_frame.grid(row=1, column=0, sticky="wens", padx=5, pady=5)

        self.match_case_checkbox = tk.Checkbutton(opt_frame, text="Match case", variable=self.matchCase_check)
        self.match_case_checkbox.grid(row=0, column=1, sticky="w")
        self.whole_word_checkbox = tk.Checkbutton(opt_frame, text="Whole word", variable=self.wholeWord_check)
        self.whole_word_checkbox.grid(row=1, column=1, sticky="w")
        self.wrap_around_checkbox = tk.Checkbutton(opt_frame, text="Wrap around", variable=self.wrapAround_check)
        self.wrap_around_checkbox.grid(row=2, column=1, sticky="w")

    def build_scope_frame(self):
        scope_frame = tk.LabelFrame(self.window, text="Scope from", padx=5, pady=5)
        scope_frame.grid(row=1, column=1, sticky="wens", padx=5, pady=5)
        tk.Radiobutton(scope_frame, text="Cursor", variable=self.scope_mode, value="cursor"
                       ).grid(row=0, column=0, sticky="w")
        tk.Radiobutton(scope_frame, text="Begin", variable=self.scope_mode, value="begin"
                       ).grid(row=1, column=0, sticky="w")

    def hide(self):
        self.window.grab_release()
        self.window.withdraw()

    def show(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_set()
        self.window.grab_set()
        return self

class SearchDialog(Dialog):
    def __init__(self, editor):
        super().__init__(editor, "SearchDialog")

    def build_buttons_frame(self):
        buttons_frame = tk.LabelFrame(self.window, text=" ", padx=5, pady=5)
        buttons_frame.grid(row=0, column=2, rowspan=2, sticky='wens', padx=5, pady=5)

        tk.Button(buttons_frame, text="Close", command = self.hide
                  ).grid(row=0, column=2, sticky="we", padx=5, pady=5)
        tk.Button(buttons_frame, text="FindUp", command= lambda: self.editor.next_match("up", self)
                  ).grid(row=1, column=2, sticky="we", padx=5, pady=5)
        tk.Button(buttons_frame, text="FindDown", command= lambda: self.editor.next_match("down", self)
                  ).grid(row=2, column=2, sticky="we", padx=5, pady=5)

class ReplaceDialog(Dialog):
    def __init__(self, editor):
        super().__init__(editor, "ReplaceDialog")

    def build_buttons_frame(self):
        buttons_frame = tk.LabelFrame(self.window, text=" ", padx=5, pady=5)
        buttons_frame.grid(row=0, column=2, rowspan=2, sticky='wens', padx=5, pady=5)

        tk.Button(buttons_frame, text="Close", command = self.hide
                  ).grid(row=0, column=2, sticky="we", padx=5, pady=5)
        tk.Button(buttons_frame, text="Replace+FindUp", command= lambda: self.editor.replace_next("up", self)
                  ).grid(row=1, column=2, sticky="we", padx=5, pady=5)
        tk.Button(buttons_frame, text="Replace+FindDown", command= lambda: self.editor.replace_next("down", self)
                  ).grid(row=2, column=2, sticky="we", padx=5, pady=5)
##        TODO:
##        Replace + ALL
        tk.Button(buttons_frame, text="ReplaceAll", command= lambda: self.editor.replace_all("up", self)
                  ).grid(row=3, column=2, sticky="we", padx=5, pady=5)
