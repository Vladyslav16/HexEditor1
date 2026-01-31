import tkinter as tk
from window import *
from EditorContext import *
from tkinter import messagebox

class EditMenu:
    HEX = 'hex'
    ASCII = 'ascii'
    
    def __init__(self, editor):
        self.editor = editor
        self.root = editor.root
        self.file_data = editor.file_data
        self.hex_text_widget = editor.hex_text_widget
        self.hex_format = editor.hex_format
        
        self.mode = tk.StringVar(value=EditMenu.ASCII)
        self.scope_mode = tk.StringVar(value="cursor")
        self.matchCase_check = tk.BooleanVar(value=False)
        self.wholeWord_check = tk.BooleanVar(value=False)
        self.wrapAround_check = tk.BooleanVar(value=True)

 
        self.string_ascii = tk.StringVar()
        self.string_hex = tk.StringVar()
        
        self.last_search_pos = None
        self._last_query = None
        self._last_mode = None

        self.search_dialog = tk.Toplevel(self.root)
        self.search_dialog.title("Search Dialog")
        self.search_dialog.resizable(False, False)
        self.search_dialog.transient(self.root)
        self.search_dialog.withdraw()

        self.build_search_dialog(self.search_dialog)

        self.search_dialog.protocol(
            "WM_DELETE_WINDOW",
            lambda window=self.search_dialog: self.hide_dialog(window)
        )

        self.replace_dialog = tk.Toplevel(self.root)
        self.replace_dialog.title("Replace Dialog")
        self.replace_dialog.resizable(False, False)
        self.replace_dialog.transient(self.root)
        self.replace_dialog.withdraw()

        self.build_replace_dialog(self.replace_dialog)

        self.replace_dialog.protocol(
            "WM_DELETE_WINDOW",
            lambda window=self.replace_dialog: self.hide_dialog(window)
        )

        self.dialog_type = None
        self.ascii_entry = None
        self.hex_entry = None
        self.whole_word_checkbox = None
        

    def on_open_file(self, file_data):
        self.file_data = file_data
        self.last_search_pos = None

    def show_dialog(self, dialog_type: str):
        dialogs = {
                "search": self.search_dialog,
                "replace": self.replace_dialog
            }
        dialog = dialogs.get(dialog_type)
       
        if dialog_type:
            try:
                self.dialog_type = dialog_type
                self.ascii_entry = getattr(self, f"{self.dialog_type}_ascii_entry")
                self.hex_entry = getattr(self, f"{self.dialog_type}_hex_entry")
                self.whole_word_checkbox = getattr(self, f"{self.dialog_type}_whole_word_checkbox")

                self.get_selection()
                self.on_mode_change()

                dialog.deiconify()
                dialog.lift()
                dialog.focus_set()
                dialog.grab_set()   
            except AttributeError:  
                print(f'There are no widgets for this "{self.dialog_type}" dialog.')
                return
                  
    def build_search_dialog(self, parent):
## Frame Find
        find_frame = tk.LabelFrame(
            parent,
            text="Find",
            padx=5,
            pady=5
        )
        find_frame.grid(row=0, column=0, columnspan=2, sticky="wens", padx=5, pady=5)
        
        tk.Radiobutton(find_frame, text = "Text string", variable=self.mode, value=EditMenu.ASCII, command=self.on_mode_change
                       ).grid(row=0, column=0, sticky='w', padx=0, pady=0)
        tk.Radiobutton(find_frame, text = "Hex string", variable=self.mode, value=EditMenu.HEX, command=self.on_mode_change
                       ).grid(row=2, column=0, sticky='w', padx=0, pady=0)

        tk.Button(find_frame, text="Text->Hex",  width=8, height=1, command=self.text_to_hex
                  ).grid(row=0, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        tk.Button(find_frame, text="Hex->Text", width=8, height=1, command=self.hex_to_text
                  ).grid(row=2, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        
        self.search_ascii_entry = tk.Entry(find_frame, textvariable=self.string_ascii, width=50)
        self.search_ascii_entry.grid(row=1, column=0, columnspan=3, sticky="we", padx=0, pady=0)
        
        self.search_hex_entry = tk.Entry(find_frame, textvariable=self.string_hex)
        self.search_hex_entry.grid(row=3, column=0, columnspan=3, sticky="we", padx=0, pady=0)
        
## Frame Options
        opt_frame = tk.LabelFrame(
                    parent,
                    text="Options",
                    padx=5,
                    pady=5
                )
        opt_frame.grid(row=1, column=0, sticky="wens", padx=5, pady=5)

        self.search_match_case_checkbox = tk.Checkbutton(opt_frame, text="Match case", variable=self.matchCase_check)
        self.search_match_case_checkbox.grid(row=0, column=1, sticky="w")
        self.search_whole_word_checkbox = tk.Checkbutton(opt_frame, text="Whole word", variable=self.wholeWord_check)
        self.search_whole_word_checkbox.grid(row=1, column=1, sticky="w")
        self.search_wrap_around_checkbox = tk.Checkbutton(opt_frame, text="Wrap around", variable=self.wrapAround_check)
        self.search_wrap_around_checkbox.grid(row=2, column=1, sticky="w")
        
## Frame Scope from
        scope_frame = tk.LabelFrame(
            parent,
            text="Scope from",
            padx=5,
            pady=5
        )
        scope_frame.grid(row=1, column=1, sticky="wens", padx=5, pady=5)
        
        tk.Radiobutton(scope_frame, text="Cursor", variable=self.scope_mode, value="cursor"
                       ).grid(row=0, column=0, sticky="w")
        tk.Radiobutton(scope_frame, text="Begin", variable=self.scope_mode, value="begin"
                       ).grid(row=1, column=0, sticky="w")
## Frame Buttons
        buttons_frame = tk.LabelFrame(
            parent,
            text=" ",
            padx=5,
            pady=5
        )
        buttons_frame.grid(row=0, column=2, rowspan=2, sticky='wens', padx=5, pady=5)

        tk.Button(buttons_frame, text="Close", command=lambda window=parent: self.hide_dialog(window)
                  ).grid(row=0, column=2, sticky="we", padx=5, pady=5)
        tk.Button(buttons_frame, text="FindDown", command=lambda: self.next_match("down")
                  ).grid(row=1, column=2, sticky="we", padx=5, pady=5)
        tk.Button(buttons_frame, text="FindUp", command=lambda: self.next_match("up")
                  ).grid(row=2, column=2, sticky="we", padx=5, pady=5)

        

    def get_search_options(self):
        class Options:
            def __init__(self, dialog:EditMenu):
                self.case  = dialog.matchCase_check.get()
                self.word  = dialog.wholeWord_check.get()
                self.wrap  = dialog.wrapAround_check.get()
                self.scope = dialog.scope_mode.get()
                self.mode  = dialog.mode.get()
        return Options(self)
        
    def on_mode_change(self):
        if self.mode.get() == EditMenu.ASCII:
            self.ascii_entry.config(state="normal")
            self.whole_word_checkbox.config(state="normal")
            self.hex_entry.config(state="disabled")
            self.ascii_entry.focus_set()
            self.ascii_entry.icursor(tk.END)
        else:
            self.wholeWord_check.set(False)
            self.whole_word_checkbox.config(state="disabled")
            self.ascii_entry.config(state="disabled")
            self.hex_entry.config(state="normal")
            self.hex_entry.focus_set()
            self.hex_entry.icursor(tk.END)

    def text_to_hex(self):
        text = self.string_ascii.get()
        if not text:
            return

        # ASCII → HEX
        hex_str = " ".join(f"{ord(c):02X}" for c in text)

        self.mode.set(EditMenu.HEX)
        self.on_mode_change()

        self.string_hex.set(hex_str)
        self.hex_entry.focus_set()
        self.hex_entry.icursor(tk.END)

    def hex_to_text(self):
        _hex = self.string_hex.get().strip()
        if not _hex:
            return

        # HEX → ASCII
        data = bytes.fromhex(_hex)
        text_str = ''.join(
            chr(b) if 0x20 <= b <= 0x7E else '.'
            for b in data
            )

        self.mode.set(EditMenu.ASCII)
        self.on_mode_change()

        self.string_ascii.set(text_str)
        self.ascii_entry.focus_set()
        self.ascii_entry.icursor(tk.END)
        
    def hide_dialog(self, window: tk.Toplevel):
        window.grab_release()
        window.withdraw()

    def get_selection(self):
        try:
            selection_begin = self.hex_text_widget.index(tk.SEL_FIRST)
            selection_end = self.hex_text_widget.index(tk.SEL_LAST)
        except tk.TclError:
            return "", EditMenu.ASCII
        
        row1, col1 = map(int, selection_begin.split('.'))
        byte_first = self.hex_format.position_to_byte(row1, col1)
        row2, col2 = map(int, selection_end.split('.'))
        byte_last = self.hex_format.position_to_byte(row2, col2)

        self.mode.set((EditMenu.HEX, EditMenu.ASCII)[col1 >= self.hex_format.tail_pos])
        self.on_mode_change()
        
        data = self.file_data[byte_first:byte_last]

        if not data: return "", self.mode.get()

        if self.mode.get() == EditMenu.HEX:
            selected_str = bytes_to_hex(data)
            self.string_hex.set(selected_str)
            print('Selected hex:', selected_str)
        else: 
            selected_str = bytes_to_str(data)
            self.string_ascii.set(selected_str)
            print('Selected text:', selected_str)

        return selected_str, self.mode.get()        
        
    def search_query(self, query, mode):
        if not query:
            return None
        query = query.strip()
        if mode == EditMenu.HEX:
            query = query.replace(" ", "")
            if len(query) % 2 != 0:
                return None
            return bytearray.fromhex(query)

        return bytearray(query, "ascii")

    def next_match(self, direction):
        options = self.get_search_options()
        
        mode = self.mode.get()
        query = self.string_ascii.get() if mode == EditMenu.ASCII else self.string_hex.get()
        
##        if not query:
##            query, mode = self.get_selection()
        if not query:
            return

        search_bytes = self.search_query(query, mode)
        
        if not search_bytes or not self.file_data:
            return

        print('Last search pos:', self.last_search_pos)
        
        data_len = len(self.file_data)
        search_bytes_len = len(search_bytes)

        if self.last_search_pos is None:
            index = self.hex_text_widget.index(tk.SEL_FIRST)
            row, col = map(int, index.split("."))
            self.last_search_pos = self.hex_format.position_to_byte(row, col)
            print('Last search pos changed to:', self.last_search_pos)

        start_index = 0 if options.scope == "begin" else self.last_search_pos

        found = None
        rng = (range(start_index + 1, data_len - search_bytes_len + 1) if direction == "down"
        else range(start_index - 1, -1, -1))
            
        for i in rng:
            if self.file_data[i:i+search_bytes_len] == search_bytes:
                found = i
                break
            
        if found is None and options.wrap:
            # До кінця не знайшли. Шукаємо з початку
            rng = (range(0, start_index) if direction == "down"
            else range(data_len - search_bytes_len, start_index, -1))
                
            for i in rng:
                if self.file_data[i:i+search_bytes_len] == search_bytes:
                    found = i
                    break

        if found is not None:
            print('Last search pos:', self.last_search_pos, 'found:', found)
            self.last_search_pos = found
            # Підсвітка
            self.hex_format.clear_highlight(self.hex_text_widget, Highlight.SELECTED)
            bytes_hl.data[Highlight.SELECTED].bytes.clear()
            
            for b in range(found, found + search_bytes_len):
                bytes_hl.data[Highlight.SELECTED].bytes.add(b)
                
            self.hex_format.highlight(self.hex_text_widget, Highlight.SELECTED)
            line, hex_start_col, hex_end_col, ascii_start_col = self.hex_format.byte_coloring_positions(found)
            self.hex_text_widget.mark_set(tk.INSERT, f"{line}.{hex_start_col}")
            self.hex_text_widget.see(f"{line}.{hex_start_col}")
        else:
            tk.messagebox.showinfo("!", "No matches found.")

    def find_again(self):
        pass

    def build_replace_dialog(self, parent):
## Frame Find+Replace
        find_frame = tk.LabelFrame(
            parent,
            text="Find",
            padx=5,
            pady=5
        )
        find_frame.grid(row=0, column=0, columnspan=2, sticky="wens", padx=5, pady=5)
        
        tk.Radiobutton(find_frame, text = "Text string", variable=self.mode, value=EditMenu.ASCII, command=self.on_mode_change
                       ).grid(row=0, column=0, sticky='w', padx=0, pady=0)
        tk.Radiobutton(find_frame, text = "Hex string", variable=self.mode, value=EditMenu.HEX, command=self.on_mode_change
                       ).grid(row=2, column=0, sticky='w', padx=0, pady=0)

        tk.Button(find_frame, text="Text->Hex",  width=8, height=1, command=self.text_to_hex
                  ).grid(row=0, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        tk.Button(find_frame, text="Hex->Text", width=8, height=1, command=self.hex_to_text
                  ).grid(row=2, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        
        self.replace_ascii_entry = tk.Entry(find_frame, textvariable=self.string_ascii)
        self.replace_ascii_entry.grid(row=1, column=0, columnspan=3, sticky="we", padx=0, pady=0)
        
        self.replace_hex_entry = tk.Entry(find_frame, textvariable=self.string_hex)
        self.replace_hex_entry.grid(row=3, column=0, columnspan=3, sticky="we", padx=0, pady=0)

        tk.Label(find_frame, text="Replace with:").grid(row=4, column=0, columnspan=3, sticky="w", padx=0, pady=0)

        self.replace_entry = tk.Entry(find_frame, textvariable=self.string_ascii, width=50)
        self.replace_entry.grid(row=5, column=0, columnspan=3, sticky="we", padx=0, pady=0)
        
## Frame Options
        opt_frame = tk.LabelFrame(
                    parent,
                    text="Options",
                    padx=5,
                    pady=5
                )
        opt_frame.grid(row=1, column=0, sticky="wens", padx=5, pady=5)

        self.replace_match_case_checkbox = tk.Checkbutton(opt_frame, text="Match case", variable=self.matchCase_check)
        self.replace_match_case_checkbox.grid(row=0, column=1, sticky="w")
        self.replace_whole_word_checkbox = tk.Checkbutton(opt_frame, text="Whole word", variable=self.wholeWord_check)
        self.replace_whole_word_checkbox.grid(row=1, column=1, sticky="w")
        self.replace_wrap_around_checkbox = tk.Checkbutton(opt_frame, text="Wrap around", variable=self.wrapAround_check)
        self.replace_wrap_around_checkbox.grid(row=2, column=1, sticky="w")
        
## Frame Scope from
        scope_frame = tk.LabelFrame(
            parent,
            text="Scope from",
            padx=5,
            pady=5
        )
        scope_frame.grid(row=1, column=1, sticky="wens", padx=5, pady=5)
        
        tk.Radiobutton(scope_frame, text="Cursor", variable=self.scope_mode, value="cursor"
                       ).grid(row=0, column=0, sticky="w")
        tk.Radiobutton(scope_frame, text="Begin", variable=self.scope_mode, value="begin"
                       ).grid(row=1, column=0, sticky="w")
## Frame Buttons
        buttons_frame = tk.LabelFrame(
            parent,
            text=" ",
            padx=5,
            pady=5
        )
        buttons_frame.grid(row=0, column=2, rowspan=2, sticky='wens', padx=5, pady=5)

        tk.Button(buttons_frame, text="Close", command=lambda window=parent: self.hide_dialog(window)
                  ).grid(row=0, column=2, sticky="we", padx=5, pady=5)
        tk.Button(buttons_frame, text="Replace+FindDown", command=lambda: self.next_match("down")
                  ).grid(row=1, column=2, sticky="we", padx=5, pady=5)
        tk.Button(buttons_frame, text="Replace+FindUp", command=lambda: self.next_match("up")
                  ).grid(row=2, column=2, sticky="we", padx=5, pady=5)
##        TODO:
##        Replace + ALL
        tk.Button(buttons_frame, text="ReplaceAll", command=lambda: self.next_match("up")
                  ).grid(row=3, column=2, sticky="we", padx=5, pady=5)
        
