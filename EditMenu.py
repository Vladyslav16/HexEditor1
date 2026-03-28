import tkinter as tk
from tkinter import messagebox
from Dialogs import Dialog, ASCII, HEX
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
        
        self.last_search_pos = None
        self.last_query = None
        self.last_format = None
        self.last_dialog = None
        self.last_direction = "down"

        self.dialog = Dialog(self)
        
    def create_dialog(self, dialog_type):
        if self.dialog:
            self.dialog.hide()
            
        if dialog_type == "SearchDialog":
            self.dialog.display("search")
        elif dialog_type == "ReplaceDialog":
            self.dialog.display("replace")
        else:
            return
            
        self.show_dialog()

    def show_dialog(self):
        if self.dialog:
            self.last_dialog = self.dialog
            self.get_selection(self.dialog)
            self.on_search_format_change(self.dialog)
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
        
    def on_search_format_change(self, dialog):
        if dialog.options.search_format.get() == ASCII:
            dialog.ascii_entry.config(state="normal")
            dialog.hex_entry.config(state="disabled")
            
            dialog.match_case_checkbox.config(state="normal")
            dialog.whole_word_checkbox.config(state="normal")
            
            dialog.textbutton.config(state="normal")
            dialog.hexbutton.config(state="disabled")
            
            dialog.ascii_entry.focus_set()
            dialog.ascii_entry.icursor(tk.END)
        else:
            dialog.matchCase_check.set(False)
            dialog.wholeWord_check.set(False)
            
            dialog.match_case_checkbox.config(state="disabled")
            dialog.whole_word_checkbox.config(state="disabled")
            
            dialog.ascii_entry.config(state="disabled")
            dialog.hex_entry.config(state="normal")

            dialog.textbutton.config(state="disabled")
            dialog.hexbutton.config(state="normal")
        
            dialog.hex_entry.focus_set()
            dialog.hex_entry.icursor(tk.END)

    def text_to_hex(self, dialog):
        text = dialog.string_ascii.get()
        if not text:
            return

        # ASCII → HEX
        hex_str = " ".join(f"{ord(c):02X}" for c in text)

        
        if dialog.dialog_type == "ReplaceDialog":
            replace_ascii = dialog.replace_ascii_entry.get()
            if replace_ascii:
                hex_replace = " ".join(f"{ord(c):02X}" for c in replace_ascii)
                dialog.replace_string.set("")
                dialog.replace_string.set(hex_replace)
            
        dialog.options.search_format.set(HEX)
        self.on_search_format_change(dialog)

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

        if dialog.dialog_type == "ReplaceDialog":
            hex_replace = dialog.replace_string.get().replace(" ", "")
            if hex_replace:
                data_replace = bytes.fromhex(hex_replace)
                ascii_replace = ''.join(chr(b) if 0x20 <= b <= 0x7E else '.' for b in data_replace)
                dialog.replace_string.set("")
                dialog.replace_string.set(ascii_replace)

        dialog.options.search_format.set(ASCII)
        self.on_search_format_change(dialog)

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

        dialog.options.search_format.set((HEX, ASCII)[col1 >= self.hex_format.tail_pos])
        self.on_search_format_change(dialog)

        if dialog.options.search_format.get() == ASCII:
            byte_last -= 1
        
        data = self.file_data[byte_first:byte_last + 1]

        if not data: return "", dialog.options.search_format.get()

        if dialog.options.search_format.get() == HEX:
            selected_str = bytes_to_hex(data)
            dialog.string_hex.set(selected_str)
            print('Selected hex:', selected_str)
        else: 
            selected_str = bytes_to_str(data)
            dialog.string_ascii.set(selected_str)
            print('Selected text:', selected_str)

        #Підсвітка виділеного

        self.hex_format.clear_highlight(self.hex_text_widget, Highlight.SELECTED)
        bytes_hl.data[Highlight.SELECTED].bytes.clear()
        for b in range(byte_first, byte_last + 1):
            bytes_hl.data[Highlight.SELECTED].bytes.add(b)
        self.hex_format.highlight(self.hex_text_widget, Highlight.SELECTED)

        return selected_str, dialog.options.search_format.get()        
        
    def search_query(self, query, search_format):
        if not query:
            return None
        query = query.strip()
        if search_format == HEX:
            query = query.replace(" ", "")
            if len(query) % 2 != 0:
                return None
            return bytearray.fromhex(query)

        return bytearray(query, "ascii")

    def find_in_block(self, file_data, search_bytes, going_up, dialog):
        '''
        Returns index of the found search_bytes block in the file_data
            None if search_bytes were not found
        '''
        search_bytes_len = len(search_bytes)
        file_data_len = len(file_data)
        start_index = 0

        step = -1 if going_up else 1

        data = file_data[:]
        search = search_bytes[:]

        if not dialog.matchCase_check.get() and dialog.options.search_format.get() == ASCII:
            data = data.lower()
            search = search.lower()

        if self.last_search_pos is None:
            start_index = file_data_len - search_bytes_len if going_up else 0
        else:
            start_index = self.last_search_pos - 1 if going_up else self.last_search_pos + 1

        end = -1 if going_up else file_data_len - search_bytes_len

        for i in range(start_index, end, step):
            if data[i:i+search_bytes_len] == search:
                
                if dialog.wholeWord_check.get():
                    if not self.check_whole_word(i, search_bytes_len):
                        continue
                    
                self.last_search_pos = i
                return i
            
        if dialog.wrapAround_check.get():
            if going_up:
                start_index = file_data_len - search_bytes_len
                end = self.last_search_pos
            else:
                start_index = 0
                end = self.last_search_pos
        
            for i in range(start_index, end, step):
                if data[i:i+search_bytes_len] == search:

                    if dialog.wholeWord_check.get():
                        if not self.check_whole_word(i, search_bytes_len):
                            continue
                        
                    self.last_search_pos = i
                    return i
            
        return None    

    def next_match(self, direction, dialog):
        self.last_direction = direction
        search_format = dialog.options.search_format.get()
        query = dialog.string_ascii.get() if search_format == ASCII else dialog.string_hex.get()
        
        if not query:
            return
        
        self.last_query = query
        self.last_format  = search_format

        search_bytes = self.search_query(query, search_format)
        
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

##        pdb.set_trace()
        found = self.find_in_block(self.file_data, search_bytes, direction != "down", dialog)

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
        if self.last_query is None or self.last_format is None:
            return
        if self.last_format == ASCII:
            dialog.string_ascii.set(self.last_query)
        else:
            dialog.string_hex.set(self.last_query)
            
        dialog.options.search_format.set(self.last_format)
        self.next_match(direction, dialog)

    def replace_next(self, direction, dialog):
        search_format = dialog.options.search_format.get()
        
        if search_format == ASCII:
            search_string = dialog.string_ascii.get()
            replace_string = dialog.replace_string.get()
            
        else:
            search_string = dialog.string_hex.get()
            replace_string = dialog.replace_string.get()

        search_bytes = self.search_query(search_string, search_format)
        replace_bytes = self.search_query(replace_string, search_format)

        found = self.find_in_block(self.file_data, search_bytes, direction != "down", dialog)
        
        if found is not None:
            end = found + len(search_bytes)
            self.file_data[found:end] = replace_bytes
            self.last_search_pos = found + len(replace_bytes) - 1
            self.editor.on_resize(None)

            # Підсвітка
            self.hex_format.clear_highlight(self.hex_text_widget, Highlight.SELECTED)
            bytes_hl.data[Highlight.SELECTED].bytes.clear()
            
            for b in range(found, found + len(replace_bytes)):
                bytes_hl.data[Highlight.SELECTED].bytes.add(b)
                
            self.hex_format.highlight(self.hex_text_widget, Highlight.SELECTED)
            
            line, hex_start_col, hex_end_col, ascii_start_col = \
                  self.hex_format.byte_coloring_positions(found)
            
            self.hex_text_widget.mark_set(tk.INSERT, f"{line}.{hex_start_col}")
            self.hex_text_widget.see(f"{line}.{hex_start_col}")
        else:
            tk.messagebox.showinfo("!", "No matches found.")
        

    def replace_all(self, dialog):
        pass
