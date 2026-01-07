import pdb

import tkinter as tk
from tkinter import filedialog, scrolledtext
from window import *
from EditorContext import bytes_to_str, hex_print, get_hex_format, Highlight, bytes_hl, one_byte_to_ascii

class HexEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Hex Editor")
        win_to_center(root, 760, 360)
        
        self.side = 1
        self.hex_text_widget = scrolledtext.ScrolledText(root, wrap=tk.NONE)
        self.hex_text_widget.pack(fill=tk.BOTH, expand=True)
        self.hex_format = get_hex_format(self.update_display_size())

        self.path_to_file = None
        self.file_data = bytearray()

        tags = list(self.hex_text_widget.bindtags())
        print(f'tags:{tags}')
        tags.insert(2, "post-click1")       
        print(f'tags:{tags}')
        self.hex_text_widget.bindtags(list(tags))
        
        self.root.bind("<Configure>", self.on_resize)

        
        self.hex_text_widget.bind_class("post-click1", '<Button-1>', self.scrolling)
        self.hex_text_widget.bind('<Control-z>', self.ctrl_z)
        self.hex_text_widget.bind('<Control-Z>', self.ctrl_z)
        self.hex_text_widget.bind('<Control-Shift-z>', self.shift_ctrl_z)
        self.hex_text_widget.bind('<Control-Shift-Z>', self.shift_ctrl_z)
        self.hex_text_widget.bind('<Key>', self.press_key)
        
        for key in ["Right", "Up", "Down"]:
            self.hex_text_widget.bind(f'<KeyRelease-{key}>', self.on_click)

        self.hex_text_widget.bind(f'<KeyRelease-Left>', self.on_click_left)
       
        self.commands = {
            'File': {
                'New':        {'combination': 'Ctrl+N',         'command': self.new_file},
                'Open':       {'combination': 'Ctrl+O',         'command': self.open_file},
                'Save':       {'combination': 'Ctrl+S',         'command': lambda: self.save_file(self.path_to_file)},
                'Save As':    {'combination': 'Ctrl+Shift+S',   'command': self.save_file_as},
                '-':          None,

                'Exit':       {'combination': 'Ctrl+Q',         'command': self.root.destroy}
                },
            'Edit': {
                'Find...':    {'combination': 'Ctrl+F',   'command': self.search_dialog},
                'Find Again': {'combination': 'Ctrl+G',   'command': self.find_again}
            }
            }
        self.create_menu()

    def scrolling(self, event):
        if event.type != tk.EventType.ButtonPress:
            if event.keysym == "Prior":   # PageUp
                self.hex_text_widget.yview_scroll(-1, 'pages')
            elif event.keysym == "Next":  # PageDown
                self.hex_text_widget.yview_scroll(1, 'pages')
            elif event.keysym == "Home":
                self.hex_text_widget.yview_moveto(0)
            elif event.keysym == "End":
                self.hex_text_widget.yview_moveto(1.0)
            elif event.keysym == "BackSpace":
                self.hex_text_widget.see(tk.INSERT)
            return
        
        height = self.hex_text_widget.winfo_height()
        if event.y < height / 4:
            self.hex_text_widget.yview_scroll(-1, 'units')
        elif event.y > height / 4 * 3:
            self.hex_text_widget.yview_scroll(1, 'units')
        self.on_click(event)

    def record_change(self, byte_index, old_value, new_value):
        self.hex_format.record_change(byte_index, old_value, new_value)
        
    def ctrl_z(self, event):
        byte_index, old_value, new_value = self.hex_format.undo()
        if byte_index is None: return
        self.file_data[byte_index] = old_value
        self.on_resize(event)

    def shift_ctrl_z(self, event):
        byte_index, old_value, new_value = self.hex_format.redo()
        if byte_index is None: return
        self.file_data[byte_index] = new_value
        self.on_resize(event)

    def cursor_position(self):
        if not self.hex_text_widget.winfo_exists():
            return None, None
        index = self.hex_text_widget.index("insert")
        row, col = map(int, index.split("."))
        return row, col
   
    def press_key(self, event):
        '''
            Оброблює натискання клавіш
        '''
##        print('press_key', vars(event))
##        if event.keycode != 17:
##            pdb.set_trace()

#        if event.??? in events_binded: return
            
        if event.keysym == "Tab":
            self.on_tab(event)
            return "break"
        
        if event.keysym == "space":
            self.on_space(event)
            return "break"
            
        if event.keysym == "BackSpace":
            self.scrolling(event)
            return "break"

        if event.keysym in ("Prior", "Next", "Home", "End", "Insert"):
            self.scrolling(event)
            return "break"
            
        if event.keysym in ("Left", "Right", "Up", "Down"):
            return
        
        row, col = self.cursor_position()
        byte = self.hex_format.position_to_byte(row, col)
        if byte is None:
            return "break"

        if self.can_write(event, byte):
            return "break"
    
    def on_tab(self, event):
        row, col = self.cursor_position()
        self.side = self.hex_format.where_is_cursor(row, col)
        byte_index = self.hex_format.position_to_byte(row, col)

        line, hex_start_col, hex_end_col, ascii_start_col = \
              self.hex_format.byte_coloring_positions(byte_index)

        if self.side == 1 and col < self.hex_format.tail_pos:
            index = f"{line}.{ascii_start_col}"
        else:
            index = f"{line}.{hex_start_col}"

        self.hex_text_widget.mark_set(tk.INSERT, index)
  
        self.hex_format.clear_highlight(self.hex_text_widget)
        bytes_hl.data[Highlight.SELECTED].bytes.add(byte_index)
        self.hex_format.highlight(self.hex_text_widget, Highlight.SELECTED)
        
    def on_space(self, event):
        row, col = self.cursor_position()
        self.side = self.hex_format.where_is_cursor(row, col)

        byte_index = self.hex_format.position_to_byte(row, col)
        next_byte = byte_index + 1

        line, hex_start_col, hex_end_col, ascii_start_col = \
              self.hex_format.byte_coloring_positions(next_byte)

        if self.side == 1:
            index = f"{line}.{hex_start_col}"
        else:
            index = f"{line}.{ascii_start_col}"
            
        self.hex_text_widget.mark_set(tk.INSERT, index)
        self.hex_format.clear_highlight(self.hex_text_widget)
        bytes_hl.data[Highlight.SELECTED].bytes.add(next_byte)
        self.hex_format.highlight(self.hex_text_widget, Highlight.SELECTED)

    def can_write(self, event, byte):
        is_valid = self.edit(event, byte)
        try:
            if is_valid:
                bytes_hl.data[Highlight.CHANGED].bytes.add(byte)
                self.hex_format.highlight(self.hex_text_widget, Highlight.CHANGED)
        except Exception as err:
            print('ERROR: Invalid symbol -', err)
            is_valid = False
        return is_valid
 
    def edit(self, event, byte):
#        pdb.set_trace()
        if not event.char or not event.char.isprintable():
            return False
        if byte is None or byte >= len(self.file_data):
            return False

        row, hex_col, hex_col_end, tail_col = \
             self.hex_format.byte_coloring_positions(byte)

        next_byte = byte + 1
        nline, nhex_start_col, nhex_end_col, nascii_start_col = \
              self.hex_format.byte_coloring_positions(next_byte)

        if self.side == 1:
            nindex = f"{nline}.{nhex_start_col}"
        else:
            nindex = f"{nline}.{nascii_start_col}"

        move = False

        byte_data = None
        byte_str = None
        cursor_col = self.cursor_position()[1]
        old_value = self.file_data[byte]
        
        # if (курсор на стороні шістнадцяткової частини)
        if self.side == 1:
            if event.char in '0123456789abcdefABCDEF':
                # Hex side
                byte_data = self.file_data[byte]
                byte_str = list(f'{byte_data:02X}')
                
                byte_str[int(cursor_col != hex_col)] = event.char.upper()
                
                byte_str = ''.join(byte_str)
                byte_data = int(byte_str, 16)
            else:
                return True

            # if (курсор на стороні хвоста)
        if self.side == 2:
            if 0x1F < ord(event.char) < 0x80:
                byte_data = ord(event.char)
                byte_str  = f'{byte_data:02X}'
            else:
                return True

        self.hex_text_widget.replace(f'{row}.{hex_col}',
                                                f'{row}.{hex_col_end}',
                                                byte_str)
        self.file_data[byte] = byte_data
        self.hex_text_widget.replace(f'{row}.{tail_col}',
                                                f'{row}.{tail_col+1}',
                                                one_byte_to_ascii(byte_data))
        
        self.record_change(byte, old_value, byte_data)

        if self.side == 1:
            self.hex_text_widget.mark_set(tk.INSERT, f"{row}.{cursor_col + 1}")

            if hex_col_end - 1 <= cursor_col <= hex_col_end:
                move = True
            if cursor_col == self.hex_format.sep_pos - 1:
                move = True
            if self.hex_format.tail_pos - 3 <= cursor_col < self.hex_format.tail_pos:
                move = True
        elif self.side == 2:
            if cursor_col >= self.hex_format.tail_pos:
                move = True

        if move == True:
            self.hex_text_widget.mark_set(tk.INSERT, nindex)
            self.hex_format.clear_highlight(self.hex_text_widget)
            bytes_hl.data[Highlight.SELECTED].bytes.add(next_byte)
            self.hex_format.highlight(self.hex_text_widget, Highlight.SELECTED)
 
        return True
        
    def on_resize(self, event):
        '''
            Зміна к-сті байтів на рядок відносно розміру вікна
        '''
        if self.file_data:
            self.hex_format = get_hex_format(self.update_display_size())
            self.show_file()
            self.restore_highlight()
               
    def update_display_size(self):
        '''
            Повертає ширину текстового поля
        '''
        return self.hex_text_widget.winfo_width()

    def open_file(self):
        '''
            Відкриває файл і відображає його в hex-форматі
        '''
        path = filedialog.askopenfilename(title="Please enter the file name",
                                          filetypes=[("All", "*.*"), ("Python", "*.py")])
        if path:
            self.root.title(f'Hex Editor - {path}')
            self.path_to_file = path
            print(f'Trying to open file: {path}')
            try:
                with open(path, 'rb') as f:
                    self.file_data = bytearray(f.read())
                self.on_resize(None)
                
            except FileNotFoundError as err:
                print(f'{err}')

    def new_file(self):
        pass
##        '''
##            Створює нове пусте вікно редактора
##        '''
##        new_root = tk.Toplevel(self.root)
##        HexEditor(new_root)
##        self.path_to_file = None
##        new_root.title(f"Hex Editor")

    def save_file(self, path=None):
        if not path:
            self.save_file_as()
        with open(path, "wb") as f:
            f.write(self.file_data)
        self.path_to_file = path
 
    def save_file_as(self):
        path = filedialog.asksaveasfilename(title="Save As",
                                            filetypes=[("All Files", "*.*")])
        if path:  
            with open(path, "wb") as f:
                f.write(self.file_data)
            self.root.title(f"Hex Editor - {path}")
            self.path_to_file = path

    def search_dialog(self):
        self.selected_text = self.get_selected_text()

        if hasattr(self, "find_window") and self.find_window.winfo_exists():
            self.find_window.lift()
            self.find_window.focus_set()
            return
        self.find_window = tk.Toplevel(self.root)
        self.find_window.title("Search Dialog")
        self.find_window.resizable(False, False)
        self.find_window.transient(self.root)
        self.find_window.grab_set()
        
## Frame Find
        self.find_frame = tk.LabelFrame(
            self.find_window,
            text="Find",
            padx=5,
            pady=5
        )
        self.find_frame.grid(row=0, column=0, columnspan=3, rowspan=2, sticky="wens", padx=5, pady=5)
        
        self.mode = tk.StringVar(value="ascii")
        tk.Radiobutton(self.find_frame, text = "Text string", variable=self.mode, value="ascii", command=self.on_mode_change).grid(row=0, column=0, sticky='w', padx=0, pady=0)
        tk.Radiobutton(self.find_frame, text = "Hex string", variable=self.mode, value="hex", command=self.on_mode_change).grid(row=2, column=0, sticky='w', padx=0, pady=0)

        tk.Button(self.find_frame, text="Text->Hex",  width=8, height=1, command=self.text_to_hex
                  ).grid(row=0, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        tk.Button(self.find_frame, text="Hex->Text", width=8, height=1, command=self.hex_to_text
                  ).grid(row=2, column=1, columnspan=2, sticky='we', padx=1, pady=1)
        
        self.string_ascii = tk.StringVar()
        self.ascii_entry = tk.Entry(self.find_frame, textvariable=self.string_ascii, width=45)
        self.ascii_entry.grid(row=1, column=0, columnspan=3, sticky="w", padx=0, pady=0)
        
        self.string_hex = tk.StringVar()
        self.hex_entry = tk.Entry(self.find_frame, textvariable=self.string_hex, width=45)
        self.hex_entry.grid(row=3, column=0, columnspan=3, sticky="w", padx=0, pady=0)
        
## Frame Options
        self.find_frame2 = tk.LabelFrame(
                    self.find_window,
                    text="Options",
                    padx=5,
                    pady=5
                )
        self.find_frame2.grid(row=2, column=0, columnspan=2, sticky="wens", padx=5, pady=5)

        self.matchCase_check = tk.BooleanVar(value=False)
        self.wholeWord_check = tk.BooleanVar(value=False)
        self.wrapAround_check = tk.BooleanVar(value=False)

        checkbox = tk.Checkbutton(self.find_frame2, text="Match case",  variable=self.matchCase_check).grid(row=0, column=1, sticky="w")
        checkbox = tk.Checkbutton(self.find_frame2, text="Whole word",  variable=self.wholeWord_check).grid(row=1, column=1, sticky="w")
        checkbox = tk.Checkbutton(self.find_frame2, text="Wrap around", variable=self.wrapAround_check).grid(row=2, column=1, sticky="w")
        
## Frame Scope from
        self.find_frame3 = tk.LabelFrame(
            self.find_window,
            text="Scope from",
            padx=5,
            pady=5
        )
        self.find_frame3.grid(row=2, column=2, columnspan=2, sticky="wens", padx=5, pady=5)
        self.scope_mode = tk.StringVar(value="cursor")
        tk.Radiobutton(self.find_frame3, text="Cursor", variable=self.scope_mode, value="cursor").grid(row=0, column=3, sticky="w")
        tk.Radiobutton(self.find_frame3, text="Begin", variable=self.scope_mode, value="begin").grid(row=1, column=3, sticky="w")

        tk.Button(self.find_window, text="Next", width=6, command=lambda: self.next_match("down")
                  ).grid(row=3, column=0, columnspan=1, sticky="we", padx=5, pady=5)
        tk.Button(self.find_window, text="Prev", width=6, command=lambda: self.next_match("up")
                  ).grid(row=3, column=1, columnspan=1, sticky="we", padx=5, pady=5)
        tk.Button(self.find_window, text="Cancel", width=6, command=self.on_close_search
                  ).grid(row=3, column=2, columnspan=1, sticky="we", padx=5, pady=5)
        
        self.hex_text_widget.tag_remove("search_match", "1.0", tk.END)
        self.last_search_pos = 0
        self.find_window.protocol("WM_DELETE_WINDOW", self.on_close_search)

    def get_search_options(self):
            return {
                "_case":  self.matchCase_check.get(),
                "_word":  self.wholeWord_check.get(),
                "_wrap":  self.wrapAround_check.get(),
                "_scope": self.scope_mode.get(),
                "_mode": self.mode.get(),
            }
        
    def on_mode_change(self):
        if self.mode.get() == "ascii":
            self.ascii_entry.config(state="normal")
            self.hex_entry.config(state="disabled")
            self.ascii_entry.focus_set()
        else:
            self.ascii_entry.config(state="disabled")
            self.hex_entry.config(state="normal")
            self.hex_entry.focus_set()

    def text_to_hex(self):
        text = self.string_ascii.get()
        if not text:
            return

        # ASCII → HEX
        hex_str = " ".join(f"{ord(c):02X}" for c in text)

        self.mode.set("hex")
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
        text_str = data.decode("ascii")

        self.mode.set("ascii")
        self.on_mode_change()

        self.string_ascii.set(text_str)
        self.ascii_entry.focus_set()
        self.ascii_entry.icursor(tk.END)
        
    def on_close_search(self):
        self.selected_text = None
        self.find_window.grab_release()
        self.find_window.destroy()

    def get_search_string(self):
        selected = self.selected_text
        if selected:
            _str = selected.replace(" ", "").strip()
            if len(_str) >=2 and len(_str) % 2 == 0 \
               and all(c in "0123456789ABCDEFabcdef " for c in _str):
                self.string_hex.set(_str)
                return _str, "hex"

            self.string_ascii.set(_str)
            return _str, "ascii"
        
        if self.mode.get() == "ascii":
            return self.string_ascii.get(), "ascii"
        else:
            return self.string_hex.get(), "hex"

    def get_selected_text(self):
        try:
            selected_text = self.hex_text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            selection_begin = self.hex_text_widget.index(tk.SEL_FIRST)
            selection_end = self.hex_text_widget.index(tk.SEL_LAST)
            self.get_selection() # <=== Temp! For test only!
            return selected_text
        except tk.TclError:
            return ''

    def get_selection(self):
        # Combination of get_search_string and get_selected_text

        # Get raw
        try:
            selection_begin = self.hex_text_widget.index(tk.SEL_FIRST)
            selection_end = self.hex_text_widget.index(tk.SEL_LAST)
        except tk.TclError:
            return '', 'hex'
        row, col = map(int, selection_begin.split('.'))
        byte_first = self.hex_format.position_to_byte(row, col)
        row, col = map(int, selection_end.split('.'))
        byte_last = self.hex_format.position_to_byte(row, col)
        selected_text = bytes_to_str(self.file_data[byte_first:byte_last+1])
        selected_hex = ' '.join([f'{b:0X}' for b in self.file_data[byte_first:byte_last+1]])
        print('Selected text:', selected_text)
        print('Selected hex:', selected_hex)
        
    def search_query(self, query, mode):
        query = query.strip()
        if not query:
            return None
        if mode == "hex":
            hex_check = query.replace(" ", "")
            if len(hex_check) % 2 != 0:
                return None
            return bytearray.fromhex(hex_check)

        return bytearray(query, "ascii")

    def next_match(self, direction):
        options = self.get_search_options()
        query, mode = self.get_search_string()
        search_bytes = self.search_query(query, mode)
        
        if not search_bytes or not self.file_data:
            return
        
        data_len = len(self.file_data)
        
        if options["_scope"]=="begin":
            start_index = 0 if direction == "down" else data_len - 1
        else:
            start_index = self.last_search_pos

        found = None
        if direction == "down":
            rng = range(start_index, data_len - len(search_bytes) + 1)
        else:
            rng = range(start_index, -1, -1)
            
        for i in rng:
            if self.file_data[i:i+len(search_bytes)] == search_bytes:
                found = i
                break
            
        if found is None and options["_wrap"]:
            # До кінця не знайшли. Шукаємо з початку
            if direction == "down":
                rng = range(0, start_index)
            else:
                rng = range(data_len - len(search_bytes), start_index, -1)
                
            for i in rng:
                if self.file_data[i:i+len(search_bytes)] == search_bytes:
                    found = i
                    break

        if found is not None:
            if direction == "down":
                self.last_search_pos = found + 1
            else:
                self.last_search_pos = found - 1
            # Підсвітка
            self.hex_format.clear_highlight(self.hex_text_widget, Highlight.SELECTED)
            bytes_hl.data[Highlight.SELECTED].bytes.clear()
            
            for b in range(found, found + len(search_bytes)):
                bytes_hl.data[Highlight.SELECTED].bytes.add(b)
                
            self.hex_format.highlight(self.hex_text_widget, Highlight.SELECTED)
            line, hex_start_col, hex_end_col, ascii_start_col = self.hex_format.byte_coloring_positions(found)
            self.hex_text_widget.mark_set(tk.INSERT, f"{line}.{hex_start_col}")
            self.hex_text_widget.see(f"{line}.{hex_start_col}")
        else:
            tk.messagebox.showinfo("!", "No matches found.")

    def find_again(self):
        pass
    
    def show_file(self):
        self.hex_data = hex_print(self.file_data, self.update_display_size())
        self.hex_text_widget.delete("1.0", tk.END)
        self.hex_text_widget.insert(tk.END, self.hex_data)

    def restore_highlight(self):
        '''
            Відновлення підсвітки байтів
        '''
        for tag, hl in bytes_hl.data.items():
            indexes = hl.bytes
            if tag == Highlight.SELECTED and indexes:
                idx = next(iter(indexes))
                coords = self.hex_format.byte_to_tkinter_coords(idx, self.side)
                self.hex_text_widget.mark_set(tk.INSERT, coords)   
            self.hex_format.highlight(self.hex_text_widget, tag)

    def on_click_helper(self, event, direction):
        row, col = self.cursor_position()
        self.side = self.hex_format.where_is_cursor(row, col)
        
        self.hex_format.clear_highlight(self.hex_text_widget)

        byte_index = self.hex_format.position_to_byte(row, col)
        print('byte_index', byte_index)

        # Cursor correction
        line, hex_start_col, hex_end_col, ascii_start_col = \
              self.hex_format.byte_coloring_positions(byte_index)
        print((line, hex_start_col, hex_end_col, ascii_start_col))
        
        col = max(col, hex_start_col)

        if self.hex_format.tail_pos - 3 < col < self.hex_format.tail_pos:
            col = self.hex_format.hex_pos
            row += direction
            byte_index += direction
        if col >= self.hex_format.line_len:
            col = self.hex_format.tail_pos
            row += direction
            byte_index += direction
            
        self.hex_text_widget.mark_set(tk.INSERT, f'{row}.{col}')
        
        if byte_index is not None:
            bytes_hl.data[Highlight.SELECTED].bytes.add(byte_index)
            self.hex_format.highlight(self.hex_text_widget, Highlight.SELECTED)
            print('Clicked:', byte_index)

    def on_click(self, event):
        self.on_click_helper(event, 1)
            
    def on_click_left(self, event):
        row, col = self.cursor_position()
        self.side = self.hex_format.where_is_cursor(row, col)

        byte_index = self.hex_format.position_to_byte(row, col)
        print("from", byte_index)

##        pdb.set_trace()
        if byte_index is not None:

            print("Current byte", byte_index)
            prev_byte = byte_index - 1
            print("Previous byte", byte_index)
            line, hex_start_col, hex_end_col, ascii_start_col = self.hex_format.byte_coloring_positions(byte_index)
            pline, phex_start_col, phex_end_col, pascii_start_col = self.hex_format.byte_coloring_positions(prev_byte)
            print((line, hex_start_col, hex_end_col, ascii_start_col))

            if self.side == 1:
                if col < self.hex_format.hex_pos:
                    line -= 1
                    col = self.hex_format.tail_pos - 3
                    byte_index -= 1  
                elif self.hex_format.sep_pos - 1 <= col <= self.hex_format.sep_pos + 1:
                    col = phex_end_col
                    byte_index -= 1
      
            elif self.side == 2:
                if col < self.hex_format.tail_pos:
                    line -= 1
                    col = self.hex_format.line_len - 1
                    byte_index -= 1            
                    
            new_pos = f"{line}.{col}"

            self.hex_text_widget.mark_set(tk.INSERT, new_pos)

            curr_byte = self.hex_format.position_to_byte(line, col)
            
            self.hex_format.clear_highlight(self.hex_text_widget, Highlight.SELECTED)
            bytes_hl.data[Highlight.SELECTED].bytes.add(curr_byte)
            self.hex_format.highlight(self.hex_text_widget, Highlight.SELECTED)
        
    def create_menu(self):
            menu = tk.Menu(self.root)
            for group, group_commands in self.commands.items():
                m = tk.Menu(menu, tearoff=0)
                for action, data in group_commands.items():
                    if action == '-':
                        m.add_separator()
                        continue
                    m.add_command(label=action,
                                  accelerator=data['combination'],
                                  command=data['command'])
                    if 'combination' in data and data['combination']:
                        comb = data.get('combination')
                        key = comb.split("+")[-1].lower()
                        if 'shift' in comb.lower():
                            pattern_1 = f"<Control-Shift-{key.lower()}>"
                            pattern_2 = f"<Control-Shift-{key.upper()}>"
                        else:
                            pattern_1 = f"<Control-{key.lower()}>"
                            pattern_2 = f"<Control-{key.upper()}>"
                        self.root.bind(pattern_1, lambda e, cmd=data['command']: cmd())
                        self.root.bind(pattern_2, lambda e, cmd=data['command']: cmd())
                            
                menu.add_cascade(label=group, menu=m)
            self.root.config(menu=menu)

if __name__ == "__main__":
    root = tk.Tk()
    app = HexEditor(root)
    root.mainloop()
