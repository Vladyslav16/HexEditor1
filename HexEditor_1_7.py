import pdb

import tkinter as tk
from tkinter import filedialog, scrolledtext
from window import *
from helpers_0_2 import *
from Editor_context_0_3 import EditorContext

class HexEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Hex Editor")
        win_to_center(root, 600, 300)

        self.hex_text_widget = scrolledtext.ScrolledText(root, wrap=tk.NONE)
        self.hex_text_widget.pack(fill=tk.BOTH, expand=True)
        self.ed_context = EditorContext(self.hex_text_widget)

        self.hex_text_widget.bind("<Key>", self.onKey)

        for key in ["Left", "Right", "Up", "Down"]:
            self.hex_text_widget.bind(f'<KeyRelease-{key}>', self.onKeyArrow)

        self.bytes_per_line = 0
        self.path_to_file = None
        self.file_data = bytearray()

        self.commands = {
            'File': {
                'New':        {'combination': 'Ctrl+N',         'command': self.new_file},
                'Open':       {'combination': 'Ctrl+O',         'command': self.open_file},
                'Save':       {'combination': 'Ctrl+S',         'command': lambda: self.save_file(self.path_to_file)},
                'Save As':    {'combination': 'Ctrl+Shift+S',   'command': self.save_file_as},
                '-':          None,
                'Exit':       {'combination': 'Ctrl+Q',         'command': self.root.destroy}
            },
            'Search': {
                'Find':       {'combination': 'Ctrl+F',         'command': lambda: print("Find")},
                'Find Again': {'combination': 'Ctrl+G',         'command': lambda: print("Find Again")},
                'Replace':    {'combination': 'Ctrl+H',         'command': lambda: print("Replace")}
            },
            'Edit': {
                'Print cursor position': {'combination': 'Ctrl+P', 'command': lambda: cursor_position(self)}
            },
        }

        self.root.bind("<Configure>",   self.config_event)
        self.root.bind("<Button-1>",    lambda e: cursor_position(self, e))
        self.create_menu()

    def update_display_size(self):
        '''
            Повертає ширину текстового поля
        '''
        return self.hex_text_widget.winfo_width()

    def onKeyArrow(self, event):
        '''
            Оброблює відпускання клавіш-стрілок для переміщення курсору
        '''
        print(f"Key Release: {event.keycode, event.char}")
        cursor_position(self, event)

    def onKey(self, event):
        '''
            Оброблює натискання клавіш:
            - Керує поєднаннями (Ctrl+...)
            - Вставляє введенні символи в hex/ASCII-зони
        '''
        if event.keysym in ("Left", "Right", "Up", "Down"):
            return

        key = event.keysym.lower()
        ctrl = (event.state & 0x4) != 0
        shift = (event.state & 0x1) != 0

        shortcuts = {
            ("n", True, False): self.new_file,
            ("o", True, False): self.open_file,
            ("s", True, False): lambda: self.save_file(self.path_to_file),
            ("s", True, True ): self.save_file_as,
            ("f", True, False): lambda: print("Find"),
            ("g", True, False): lambda: print("Find Again"),
            ("h", True, False): lambda: print("Replace"),
            ("q", True, False): self.root.destroy,
        }
        func = shortcuts.get((key, ctrl, shift))
        if func:
            func()
            return

        cursor_position(self, event)
        byte_number = self.ed_context.cursor_pos_to_byte_number()
        if not byte_number:
            return "break"
        pos = self.ed_context.calc_cursor_position(byte_number)
        self.bInsert(byte_number, pos, event)
        return "break"

    def new_file(self):
        '''
            Створює нове пусте вікно редактора
        '''
        new_root = tk.Toplevel(self.root)
        HexEditor(new_root)
        self.path_to_file = None
        new_root.title(f"Hex Editor")

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
                self.show_file()             
##                row, hex_col, tail_col = self.ed_context.calc_cursor_position(0)
##                self.hex_text_widget.mark_set(tk.INSERT, f'{row - 1}.{hex_col}')
            except FileNotFoundError as err:
                print(f'{err}')

    def save_file(self, path=None):
        '''
            Зберінає поточний файл. Якщо шлях не вказаний викликає - "save_file_as".
            :param path: Шлях до файлу. Якщо None — викликається діалог "Save As".
        '''
        if not path:
            path = self.save_file_as()
            if not path:
                return
        with open(path, "wb") as f:
            f.write(self.file_data)
        self.path_to_file = path

    def save_file_as(self):
        path = filedialog.asksaveasfilename(title="Save As", filetypes=[("All Files", "*.*")])
        if path:
            with open(path, "wb") as f:
                f.write(self.file_data)
            self.root.title(f"Hex Editor - {path}")
            self.path_to_file = path
            return path
        return None

    def show_file(self):
        hex_data = self.print_hex()
        self.hex_text_widget.delete("1.0", tk.END)
        self.hex_text_widget.insert(tk.END, hex_data)

    def print_hex(self):
        if not self.file_data: return ""
        res = ''
        winW = self.update_display_size()
        self.bytes_per_line = self.ed_context._bytes_from_size(winW)
        tails = chunks(self.file_data, self.bytes_per_line)
        tail = 0

        for i, c in enumerate(self.file_data.hex().upper()):
            if i % (self.bytes_per_line * 2) == 0:
                res += f'{(i//2):08}: '
            res += c
            if i % (self.bytes_per_line * 2) == (self.bytes_per_line * 2 - 1):
                res += '   ' + bytes_to_ascii(tails[tail])
                tail += 1
                res += f'\n'
            elif i == len(self.file_data)*2 - 1:
                printed = (i % (self.bytes_per_line * 2))//2+1
                res += '   ' + ' '*((self.bytes_per_line - printed) * 3 + (2 if printed <= (self.bytes_per_line // 2) else 0)) + bytes_to_ascii(tails[tail])
                tail += 1
                res += f'\n'
            elif i % self.bytes_per_line == self.bytes_per_line - 1:
                res += ' | '
            elif i % 2 == 1:
                res += ' '
        return res

    def config_event(self, e):
        context = self.ed_context
        new_window_w = self.hex_text_widget.winfo_width()
        if self.file_data and context._bytes_from_size(new_window_w) != self.bytes_per_line:
            hex_byte_num = context.cursor_pos_to_byte_number()
            if hex_byte_num is not None:
                section = context.cursor_side()
                context.on_resize()
                self.show_file()
                row, hex_col, tail_col = context.calc_cursor_position(hex_byte_num)
                context.highlight_byte(hex_byte_num, 'insert')

    def create_menu(self):
        menu = tk.Menu(self.root)
        for group, group_commands in self.commands.items():
            m = tk.Menu(menu, tearoff=0)
            for action, data in group_commands.items():
                if action == '-':
                    m.add_separator()
                else:
                    m.add_command(label=action, accelerator=data['combination'], command=data['command'])
            menu.add_cascade(label=group, menu=m)
        self.root.config(menu=menu)

    def bInsert(self, byte_number, pos, event):
        is_valid = self.edit(byte_number, pos, event)
        try:
            if is_valid:
                self.hex_text_widget.insert(tk.INSERT, event.char.upper())
                self.ed_context.highlight_byte(byte_number, 'change')
        except:
            print('invalid symbol')
        
    def edit(self, byte_number, pos, event):
        row, hex_col, tail_col = pos
        hex_index = f'{row}.{hex_col}'
        ascii_index = f'{row}.{tail_col}'

        if not event.char or not event.char.isprintable():
            return False
        if byte_number is None or byte_number >= len(self.file_data):
            return False

        # if (курсор на стороні шістнадцяткової частини)
        if self.hex_text_widget.index(tk.INSERT) == hex_index:
            if event.char in '0123456789abcdefABCDEF':
                self.hex_text_widget.delete(hex_index, f'{hex_index}+1c')
                byte_text = self.hex_text_widget.get(f'{row}.{hex_col-1}', f'{row}.{hex_col+1}')
                byte_text = f'{byte_text[0]}{event.char}{byte_text[1]}'.strip().upper()
                byte_value = int(byte_text, 16)
                self.file_data[byte_number] = byte_value
                self.hex_text_widget.replace(f'{row}.{tail_col-1}',
                                                        f'{row}.{tail_col}',
                                                        one_byte_to_ascii(byte_value))
                return True
            else:
                return False

        # if (курсор на стороні хвоста)
        if self.hex_text_widget.index(tk.INSERT) == ascii_index:
            if 0x1F < ord(event.char) < 0x80:
                self.hex_text_widget.delete(ascii_index, f'{ascii_index}+1c')
                byte_value = ord(event.char)
                self.file_data[byte_number] = byte_value
                self.hex_text_widget.replace(f'{row}.{hex_col}',
                                                        f'{row}.{hex_col+2}',
                                                        f'{byte_value:02X}')
                return True
            else:
                return False


if __name__ == "__main__":
    root = tk.Tk()
    app = HexEditor(root)
    root.mainloop()
