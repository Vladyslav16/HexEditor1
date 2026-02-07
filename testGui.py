import pdb

import tkinter as tk
from tkinter import filedialog, scrolledtext
from window import *
from EditorContext import *
from EditMenu import EditMenu


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

        self.edit_menu_obj = EditMenu(self)

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
                'Find Again': {'combination': 'Ctrl+G',   'command': self.find_again},
                'Replace...': {'combination': 'Ctrl+H',   'command': self.replace_dialog},
                
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
            self.edit_menu_obj.hex_format = self.hex_format
               
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
                    
                self.edit_menu_obj.on_open_file(self.file_data)
                self.on_resize(None)
                
            except FileNotFoundError as err:
                print(f'{err}')

    def search_dialog(self):
<<<<<<< HEAD
        self.edit_menu_obj.show_search_dialog()

    def replace_dialog(self):
        self.edit_menu_obj.show_replace_dialog()

    def find_again(self):
        self.edit_menu_obj.show_find_again()
=======
        self.edit_menu_obj.show_dialog("search")

    def replace_dialog(self):
        self.edit_menu_obj.show_dialog("replace")

    def find_again(self):
        self.edit_menu_obj.find_again()
>>>>>>> 03ef8fa61481004c46d427c8d3b2e6fecacafc03

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
