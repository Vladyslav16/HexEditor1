import tkinter as tk
from tkinter import messagebox
from Dialogs import SearchDialog, ReplaceDialog, ASCII, HEX
from window import *
from EditorContext import *
import pdb

class EditMenu:
    def __init__(self, editor):
        self.editor = editor
        self.root = editor.root
        self.file_data = editor.file_data
        self.hex_text_widget = editor.hex_text_widget
        self.hex_format = editor.hex_format
        
        self.dialog = None
        
        self.last_search_pos = None
        self.last_query = None
        self.last_mode = None
        self.last_dialog = None
        self.last_direction = "down"
        
    def create_dialog(self, dialog_type):
        dialogs_list = {
                "SearchDialog": SearchDialog,
                "ReplaceDialog": ReplaceDialog
            }
        self.dialog = dialogs_list[dialog_type](self)
        self.show_dialog()

    def show_dialog(self):
        if self.dialog:
            self.get_selection(self.dialog)
            self.on_mode_change(self.dialog)
            self.dialog.show()
       
    def on_open_file(self, file_data):
        self.file_data = file_data
        self.last_search_pos = None

    def show_find_again(self):
        last_dialog = self.last_dialog
        if last_dialog:
            print(last_dialog.dialog_type)
            self.find_again(last_dialog)
        else: return
        
        
    def on_mode_change(self, dialog):
        if dialog.options.format.get() == ASCII:
            dialog.ascii_entry.config(state="normal")
            dialog.whole_word_checkbox.config(state="normal")
            dialog.hex_entry.config(state="disabled")
            dialog.ascii_entry.focus_set()
            dialog.ascii_entry.icursor(tk.END)
        else:
            dialog.wholeWord_check.set(False)
            dialog.whole_word_checkbox.config(state="disabled")
            dialog.ascii_entry.config(state="disabled")
            dialog.hex_entry.config(state="normal")
            dialog.hex_entry.focus_set()
            dialog.hex_entry.icursor(tk.END)

    def text_to_hex(self, dialog):
        text = dialog.string_ascii.get()
        if not text:
            return

        # ASCII → HEX
        hex_str = " ".join(f"{ord(c):02X}" for c in text)

        dialog.options.format.set(HEX)
        self.on_mode_change(dialog)

        dialog.string_hex.set(hex_str)
        dialog.hex_entry.focus_set()
        dialog.hex_entry.icursor(tk.END)

    def hex_to_text(self, dialog):
        _hex = dialog.string_hex.get().strip()
        if not _hex:
            return

        # HEX → ASCII
        data = bytes.fromhex(_hex)
        text_str = ''.join(
            chr(b) if 0x20 <= b <= 0x7E else '.'
            for b in data
            )

        dialog.options.format.set(ASCII)
        self.on_mode_change(dialog)

        dialog.string_ascii.set(text_str)
        dialog.ascii_entry.focus_set()
        dialog.ascii_entry.icursor(tk.END)
        
    def get_selection(self, dialog):
        try:
            selection_begin = self.hex_text_widget.index(tk.SEL_FIRST)
            selection_end = self.hex_text_widget.index(tk.SEL_LAST)
        except tk.TclError:
            return "", ASCII
        
        row1, col1 = map(int, selection_begin.split('.'))
        byte_first = self.hex_format.position_to_byte(row1, col1)
        row2, col2 = map(int, selection_end.split('.'))
        byte_last = self.hex_format.position_to_byte(row2, col2)

        dialog.options.format.set((HEX, ASCII)[col1 >= self.hex_format.tail_pos])
        self.on_mode_change(dialog)
        
        data = self.file_data[byte_first:byte_last]

        if not data: return "", dialog.options.format.get()

        if dialog.options.format.get() == HEX:
            selected_str = bytes_to_hex(data)
            dialog.string_hex.set(selected_str)
            print('Selected hex:', selected_str)
        else: 
            selected_str = bytes_to_str(data)
            dialog.string_ascii.set(selected_str)
            print('Selected text:', selected_str)

        return selected_str, dialog.options.format.get()        
        
    def search_query(self, query, mode):
        if not query:
            return None
        query = query.strip()
        if mode == HEX:
            query = query.replace(" ", "")
            if len(query) % 2 != 0:
                return None
            return bytearray.fromhex(query)

        return bytearray(query, "ascii")

    def find_in_block(self, file_data, start_index, search_bytes, going_up, dialog):
        search_bytes_len = len(search_bytes)
        file_data_len = len(file_data)

        start_index = 0 if start_index is None else start_index
        wrap = False

        while True:
            data = file_data[start_index:]
            
            if going_up:
                data = data[::-1]
                search_bytes = search_bytes[::-1]
                
            found = None
            for i, c in enumerate(data):
                if data[i:i+search_bytes_len] == search_bytes:
                    idx = start_index + i
                    if dialog.wholeWord_check:
                        if not self.check_whole_word(idx, search_bytes_len):
                            continue
                    if going_up:
                        found = file_data_len - (idx + search_bytes_len)
                    else:
                        found = idx
                    break
                
            if found is not None:
                self._last_search_pos = found
                return found
                
            if found is None and dialog.wrapAround_check and not wrap:
                wrap = True
                start_index = 0
                continue
            break

        return None

    def next_match(self, direction, dialog):
        self._last_direction = direction
        mode = dialog.options.format.get()
        query = dialog.string_ascii.get() if mode == ASCII else dialog.string_hex.get()
        
        if not query:
            return
        
        self.last_query = query
        self.last_mode  = mode

        search_bytes = self.search_query(query, mode)
        
        if not search_bytes or not self.file_data:
            return

        print('Last search pos:', self.last_search_pos)
        
        data_len = len(self.file_data)
        search_bytes_len = len(search_bytes)

        if self.last_search_pos is None:
            try:
                index = self.hex_text_widget.index(tk.SEL_FIRST)
            except tk.TclError:
                index = self.hex_text_widget.index(tk.INSERT)
            row, col = map(int, index.split("."))
            self.last_search_pos = self.hex_format.position_to_byte(row, col)
            print('Last search pos changed to:', self.last_search_pos)

        start_index = 0 if dialog.scope_mode == "begin" else self.last_search_pos

        found = self.find_in_block(self.file_data, start_index, search_bytes, direction != "down", dialog)

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

    def check_whole_word(self, idx, search_bytes_len):
        if idx == 0:
            start_index = True
        else:
            left_sym = chr(self.file_data[idx-1])
            start_index = not left_sym.isalpha()

        if idx + search_bytes_len >= len(self.file_data):
            end_index = True
        else:
            right_sym = chr(self.file_data[idx+search_bytes_len])
            end_index = not right_sym.isalpha()

        return start_index and end_index
            
    def find_again(self, dialog):
        direction = self.last_direction
        if self.last_query is None or self.last_mode is None:
            return
        if self.last_mode == ASCII:
            dialog.string_ascii.set(self.last_query)
        else:
            dialog.string_hex.set(self.last_query)

        dialog.mode.set(self.last_mode)
        self.next_match(direction, dialog)

    def replace_next(self, dialog):
        pass

    def replace_all(self, dialog):
        pass
        
        
