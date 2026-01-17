import tkinter as tk
from window import *
from EditorContext import *

class SearchDialog:
    HEX = 'hex'
    ASCII = 'ascii'
    
    def __init__(self, editor):
        self.editor = editor
        self.root = editor.root
        self.find_window = None
        self.file_data = editor.file_data
        self.hex_text_widget = editor.hex_text_widget
        self.hex_format = editor.hex_format
        
        self.mode = tk.StringVar(value=SearchDialog.ASCII)
        self.scope_mode = tk.StringVar(value="cursor")
        self.matchCase_check = tk.BooleanVar(value=False)
        self.wholeWord_check = tk.BooleanVar(value=False)
        self.wrapAround_check = tk.BooleanVar(value=True)

        self.string_ascii = tk.StringVar()
        self.string_hex = tk.StringVar()

        self.last_search_pos = 0
        self._last_query = None
        self._last_mode = None

    def show_search_dialog(self):
        if self.find_window and self.find_window.winfo_exists():
            self.find_window.lift()
            self.find_window.focus_set()
            return

        self.find_window = tk.Toplevel(self.root)
        self.find_window.title("Search Dialog")
        self.find_window.resizable(False, False)
        self.find_window.transient(self.root)
        self.find_window.grab_set()

        self.build_dialog()
        self.get_selection()
        self.on_mode_change()
        self.find_window.protocol("WM_DELETE_WINDOW", self.on_close_search)
        
    def build_dialog(self):
## Frame Find
        self.find_frame = tk.LabelFrame(
            self.find_window,
            text="Find",
            padx=5,
            pady=5
        )
        self.find_frame.grid(row=0, column=0, columnspan=3, rowspan=2, sticky="wens", padx=5, pady=5)
        
        tk.Radiobutton(self.find_frame, text = "Text string", variable=self.mode, value=SearchDialog.ASCII, command=self.on_mode_change
                       ).grid(row=0, column=0, sticky='w', padx=0, pady=0)
        tk.Radiobutton(self.find_frame, text = "Hex string", variable=self.mode, value=SearchDialog.HEX, command=self.on_mode_change
                       ).grid(row=2, column=0, sticky='w', padx=0, pady=0)

        tk.Button(self.find_frame, text="Text->Hex",  width=8, height=1, command=self.text_to_hex
                  ).grid(row=0, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        tk.Button(self.find_frame, text="Hex->Text", width=8, height=1, command=self.hex_to_text
                  ).grid(row=2, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        
        self.ascii_entry = tk.Entry(self.find_frame, textvariable=self.string_ascii, width=45)
        self.ascii_entry.grid(row=1, column=0, columnspan=3, sticky="w", padx=0, pady=0)
        
        self.hex_entry = tk.Entry(self.find_frame, textvariable=self.string_hex, width=45)
        self.hex_entry.grid(row=3, column=0, columnspan=3, sticky="w", padx=0, pady=0)
        
## Frame Options
        self.opt_frame = tk.LabelFrame(
                    self.find_window,
                    text="Options",
                    padx=5,
                    pady=5
                )
        self.opt_frame.grid(row=2, column=0, columnspan=2, sticky="wens", padx=5, pady=5)

        checkbox = tk.Checkbutton(self.opt_frame, text="Match case", variable=self.matchCase_check
                                  ).grid(row=0, column=1, sticky="w")
        checkbox = tk.Checkbutton(self.opt_frame, text="Whole word", variable=self.wholeWord_check
                                  ).grid(row=1, column=1, sticky="w")
        checkbox = tk.Checkbutton(self.opt_frame, text="Wrap around", variable=self.wrapAround_check
                                  ).grid(row=2, column=1, sticky="w")
        
## Frame Scope from
        self.scope_frame = tk.LabelFrame(
            self.find_window,
            text="Scope from",
            padx=5,
            pady=5
        )
        self.scope_frame.grid(row=2, column=2, columnspan=2, sticky="wens", padx=5, pady=5)
        
        tk.Radiobutton(self.scope_frame, text="Cursor", variable=self.scope_mode, value="cursor"
                       ).grid(row=0, column=3, sticky="w")
        tk.Radiobutton(self.scope_frame, text="Begin", variable=self.scope_mode, value="begin"
                       ).grid(row=1, column=3, sticky="w")

        tk.Button(self.find_window, text="Next", width=6, command=lambda: self.next_match("down")
                  ).grid(row=3, column=0, columnspan=1, sticky="we", padx=5, pady=5)
        tk.Button(self.find_window, text="Prev", width=6, command=lambda: self.next_match("up")
                  ).grid(row=3, column=1, columnspan=1, sticky="we", padx=5, pady=5)
        tk.Button(self.find_window, text="Cancel", width=6, command=self.on_close_search
                  ).grid(row=3, column=2, columnspan=1, sticky="we", padx=5, pady=5)
        
        self.find_window.protocol("WM_DELETE_WINDOW", self.on_close_search)

        self.get_selection()
        self.on_mode_change()

    def get_search_options(self):
        class Options:
            def __init__(self, dialog:SearchDialog):
                self.case  = dialog.matchCase_check.get()
                self.word  = dialog.wholeWord_check.get()
                self.wrap  = dialog.wrapAround_check.get()
                self.scope = dialog.scope_mode.get()
                self.mode  = dialog.mode.get()
        return Options(self)
        
    def on_mode_change(self):
        if self.mode.get() == SearchDialog.ASCII:
            self.ascii_entry.config(state="normal")
            self.hex_entry.config(state="disabled")
            self.ascii_entry.focus_set()
            self.ascii_entry.icursor(tk.END)
        else:
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

        self.mode.set(SearchDialog.HEX)
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

        self.mode.set(SearchDialog.ASCII)
        self.on_mode_change()

        self.string_ascii.set(text_str)
        self.ascii_entry.focus_set()
        self.ascii_entry.icursor(tk.END)
        
    def on_close_search(self):
        self.selected_text = None
        if self.find_window and self.find_window.winfo_exists():
            self.find_window.grab_release()
            self.find_window.destroy()
        self.find_window = None

    def get_selection(self):
        try:
            selection_begin = self.hex_text_widget.index(tk.SEL_FIRST)
            selection_end = self.hex_text_widget.index(tk.SEL_LAST)
        except tk.TclError:
            return "", SearchDialog.ASCII
        
        row1, col1 = map(int, selection_begin.split('.'))
        byte_first = self.hex_format.position_to_byte(row1, col1)
        row2, col2 = map(int, selection_end.split('.'))
        byte_last = self.hex_format.position_to_byte(row2, col2)

        self.mode.set((SearchDialog.HEX, SearchDialog.ASCII)[col1 >= self.hex_format.tail_pos])
        self.on_mode_change()
        
        data = self.file_data[byte_first:byte_last+1]

        if not data: return "", self.mode.get()

        if self.mode.get() == SearchDialog.HEX:
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
        if mode == SearchDialog.HEX:
            query = query.replace(" ", "")
            if len(query) % 2 != 0:
                return None
            return bytearray.fromhex(query)

        return bytearray(query, "ascii")

    def next_match(self, direction):
        options = self.get_search_options()
        query, mode = None, None
        
        if self.find_window and self.find_window.winfo_exists():
            mode = self.mode.get()
            query = self.string_ascii.get() if mode == SearchDialog.ASCII else self.string_hex.get()
        else:
            query, mode = self.get_selection()

        search_bytes = self.search_query(query, mode)
        
        if not search_bytes or not self.file_data:
            return
        
        data_len = len(self.file_data)
        search_bytes_len = len(search_bytes)
        
        start_index = 0 if options.scope == "begin" else self.last_search_pos

        found = None
        rng = (range(start_index, data_len - search_bytes_len + 1) if direction == "down"
        else range(start_index, -1, -1))
            
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
            if direction == "down":
                self.last_search_pos = found + search_bytes_len
            else:
                self.last_search_pos = max(0, found - search_bytes_len)
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
