'''
Editor_context
'''
import tkinter as tk

class EditorContext:
    def __init__(self, editor_widget):
        '''
        Ініціалізує контекст редактора для hex-перегляду.

        :param editor_widget: Віджет tk.Text, який використовується для відображення hex-даних.
        '''
        self.editor_widget = editor_widget
        self.config = {
            'highlight': {
                'insert': { 'background': 'lightblue', 'foreground': 'black' },
                'change': { 'background': 'yellow'   , 'foreground': 'black' } 
            }
        }
        for tag, conf in self.config['highlight'].items():
            editor_widget.tag_config(tag, conf)


        self.on_resize()

    def cursor_side(self):
        '''
        0 - Hex side
        1 - Text side
        '''
        pos = self.editor_widget.index(tk.INSERT)
        row, col = map(int, pos.split('.'))
        return int(col >= self.tail_begin)

    def _bytes_from_size(self, winW):
        '''
        Визначає кількість байтів на рядок залежно від ширини вікна.

        :param winW: Ширина вікна у пікселях.
        :return: Кількість байтів на один рядок.
        '''
        data = ((400, 4), (700, 8), (1000, 16), (1300, 24), (10000, 32))
        for maxw, res in data:
            if winW < maxw:
                return res
        return 32

    def on_resize(self):
        '''
        Оновлює розмітку hex-редактора після зміни розміру вікна.
        Встановлює позиції hex-зони, ASCII-зони, кількість байтів у рядку.
        '''
        self.bytes_per_line = self._bytes_from_size(self.editor_widget.winfo_width())

        # Довжина адреси. Те ж саме, що і початок шістнадцяткової частини
        self.hex_begin = 10
        
        # Розмір сепаратору
        self.sep_size = 1
        
        # Розмір сепаратору хвоста
        self.tail_sep_size = 3
        
        # Позиція сепаратору
        self.sep_pos = self.hex_begin + (self.bytes_per_line * 3) // 2
        
        # Позиція кінця шістнадцяткової частини
        self.hex_end = self.hex_begin + self.bytes_per_line * 3 + self.sep_size
        
        # Позиція хвоста
        self.tail_begin = self.hex_end + self.tail_sep_size
        
        # Позиція кінця рядку
        self.tail_end = self.tail_begin + self.bytes_per_line

        _vars = {
            "bytes_per_line": self.bytes_per_line,
            "hex_begin": self.hex_begin,
            "sep_size": self.sep_size,
            "tail_sep_size": self.tail_sep_size,
            "sep_pos": self.sep_pos,
            "hex_end": self.hex_end,
            "tail_begin": self.tail_begin,
            "tail_end": self.tail_end
        }
        print("on_resize vars")
        for name, value in _vars.items():
            print(f"{name:<15}:{value:>2}")

    def cursor_pos_to_byte_number(self, pos=None):
        '''
        Cursor => Byte
        :param pos: Позиція курсору
        :return: Повертає номер байту
        '''
##        if pos is None:
##            pos = self.editor_widget.index(tk.INSERT)
##        row, col = map(int, str(pos).split('.'))
##        row_bytes = (row) * self.bytes_per_line
##
##        #Курсор в адресній частині
##        if col < self.hex_begin:
##            return None
##
##        #Курсор в сепараторі
##        if self.sep_pos <= col < self.sep_pos + self.sep_size:
##            return None
##
##        #Курсор в ASCII (tail) частині
##        if col >= self.tail_begin:
##            return row_bytes + col - self.tail_begin
##            return None
##
##        if col < self.sep_pos: # Це означає, що курсор на першій половині hex
##            return row_bytes + (col - self.hex_begin) // 3
##        else: # Це означає, що курсор на другій половині hex
##            return row_bytes + (col - self.hex_begin - self.sep_size) // 3
##        return None # Це означає, що ми не знаємо номер байту (курсор на пустому місці)

        if pos is None:
            pos = self.editor_widget.index(tk.INSERT)  
        row, col = map(int, pos.split('.'))
        
        bytes_per_line = self.bytes_per_line

        row_bytes = (row - 1) * bytes_per_line
        
        if bytes_per_line == 0:
            print('Немає байтів в рядку')
            return None
        
        hex_begin = self.hex_begin
        sep_pos = self.sep_pos
        hex_end = self.hex_end
        tail_begin = self.tail_begin 
        tail_end = self.tail_end
        

        #Курсор в адресній частині
        if col < hex_begin:
            return None
        
        #курсор в сепараторі
        if sep_pos <= col <= sep_pos + self.sep_size:
            print('Сeпаратор Hex')
            return None
        
        if hex_end < col < tail_begin:
            print('Сепаратор Tail')
            return None
        
        #курсор в ASCII(tail)
        if col >= tail_begin:
            tail_offset = row_bytes + col - tail_begin
            if tail_offset > bytes_per_line - 1:
                print('???')
                return None
            tail_byte_num = (row-1) * bytes_per_line + tail_offset
            hex_col = hex_begin + tail_offset * 3
            if tail_offset >= bytes_per_line // 2:
                hex_col += 2
            print('Tail байт')
            return tail_byte_num
            
        #курсор в hex
        if hex_end > col >= hex_begin:
            bytes_col = col - hex_begin
            
            #після сепаратору
            if col > sep_pos + self.sep_size:
                bytes_col -=2
                
            #якщо пробіл
            if bytes_col % 3 == 2:
                print('Пробіл')
                return None
             
            byte = bytes_col // 3
            byte_number = (row-1) * bytes_per_line + byte
            tail_col = tail_begin + byte
            print('Hex байт')
            return byte_number
        
    def calc_cursor_position(self, byte_number=None):
        '''
        Обчислює позицію байта у вигляді (рядок, колонка hex-зони, колонка ASCII-зони).
        Byte => Cursor

        :param byte_number: Номер байта.
        :return: Повертає кортеж (row, hex_col, tail_col)
        '''
        row = byte_number // self.bytes_per_line
        byte_in_row = byte_number % self.bytes_per_line
        sep = 0
        if byte_in_row >= self.bytes_per_line // 2:
            sep = 2
        hex_col = self.hex_begin + byte_in_row * 3 + sep
        tail_col = self.tail_begin + byte_in_row
        return (row, hex_col, tail_col)
            
    
    def calc_highlight_position(self, byte_number):
        '''
        Обчислює позиції для підсвічування байта.

        :param byte_number: Номер байта.
        :return: Кортеж із двох підкортежів:
            - hex_light: (start, end) індекси в hex-зоні для підсвічування 2 символів
            - ascii_light: (start, end) індекси в ASCII-зоні для підсвічування 1 символа
        '''
        row, hex_col, tail_col = self.calc_cursor_position(byte_number)
        hex_index = f'{row+1}.{hex_col}'
        ascii_index = f'{row+1}.{tail_col}'
        hex_light = (hex_index, f'{hex_index}+2c')
        ascii_light = (ascii_index, f'{ascii_index}+1c')
        return (hex_light, ascii_light)

    def highlight_byte(self, byte_number, tag_name):
        '''
        Підсвічує заданий байт у hex- та ASCII-зонах використовуючи заданий тег.
        
        :param byte_number: Номер байта.
        :param tag_name: Назва тегу ('insert', 'change'), 
        який буде використовуватись для підсвічування.
        '''
        hex_light, ascii_light = self.calc_highlight_position(byte_number)

        # Додаємо підсвічування
        self.editor_widget.tag_add(tag_name, *hex_light)
        self.editor_widget.tag_add(tag_name, *ascii_light)

    def clear_highlight(self, tag_name):
        '''
        Видаляє підсвічування байтів для заданого тегу.
        
        :param tag_name: Назва тегу ('insert', 'change')
        '''
        # Видаляємо старе підсвічування кольору
        self.editor_widget.tag_remove(tag_name, "1.0", "end")
