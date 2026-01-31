import pdb

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class HighlightData:
    def __init__(self, tag, color):
        self.tag = tag
        self.color = color
        self.bytes = set()

class Highlight:
    SELECTED = 'selected'
    CHANGED = 'changed'

    def __init__(self):
        self.data = {
                Highlight.SELECTED: HighlightData(Highlight.SELECTED, "lightblue"),
                Highlight.CHANGED:  HighlightData(Highlight.CHANGED, "yellow"),
            }

bytes_hl = Highlight()  

def one_byte_to_ascii(b):
    return chr(b) if 0x20 < b < 0x7E else '.'

def bytes_to_str(bytes_:list):
    return ''.join(one_byte_to_ascii(b) for b in bytes_)

def bytes_to_hex(bytes_: list):
    return ' '.join(f"{b:02X}" for b in bytes_)

def test_many_positions(lenght, *positions):
        res = [' ']*lenght
        n = 1
        for pos in positions:
            res[pos] = str(n)
            n += 1
        return ''.join(res)

class HexFormat:
    def __init__(self, winw, bytes_per_row):
        self.winw = winw
        self.bytes_per_row = bytes_per_row

        self.separator = '| '

        self.formats = [ ['', ''] ] + [
            ['{:08d}: ' + '{:02X} '*i + '   '*(bytes_per_row-i) + '  ',
             '{}'*i]
            for i in range(1, bytes_per_row+1)
            ]
        self.hex_pos  = 10
        self.tail_pos = self.hex_pos + bytes_per_row * 3 + len(self.separator) + 2
        self.sep_pos  = self.hex_pos + (bytes_per_row // 2) * 3
        self.line_len = self.tail_pos + bytes_per_row

        # Позиція ПІСЛЯ останньої зміни
        self.currentEditState = 0
        self.changeHistory = []

    def record_change(self, byte_index, old_value, new_value):
        self.changeHistory = self.changeHistory[:self.currentEditState]
        self.changeHistory.append((byte_index, old_value, new_value))
        self.currentEditState += 1
        print('History SAVE:', self.currentEditState, self.changeHistory)

    def undo(self):
        if self.currentEditState <= 0: return (None, None, None)
        self.currentEditState -= 1
        print('History UNDO:', self.currentEditState, self.changeHistory)
        return self.changeHistory[self.currentEditState]

    def redo(self):
        if self.currentEditState >= len(self.changeHistory): return (None, None, None)
        res = self.changeHistory[self.currentEditState]
        self.currentEditState += 1
        print('History REDO:', self.currentEditState, self.changeHistory)
        return res
        
    def highlight_byte(self, widget, tag, byte_index):
        hl = bytes_hl.data[tag]
        line, hex_b, hex_e, tail_b = self.byte_coloring_positions(byte_index)
        widget.tag_add(tag, f'{line}.{hex_b}', f'{line}.{hex_e}')
        widget.tag_add(tag, f'{line}.{tail_b}')
        widget.tag_config(tag, background=hl.color, foreground = "black")

    def highlight(self, widget, tag=None, byte_index = None):
        if tag is None:
            for tag in bytes_hl.data:
                self.highlight(widget, tag)
        elif byte_index is not None:
            self.highlight_byte(widget, tag, byte_index)
        else:
            hl = bytes_hl.data[tag]
            for byte_index in hl.bytes:
                self.highlight_byte(widget, tag, byte_index)
        
    def clear_highlight(self, widget, tag=Highlight.SELECTED):
        widget.tag_remove(tag, "1.0", "end")
        bytes_hl.data[tag].bytes.clear()
        
    def test_positions(self):
        return test_many_positions(self.line_len,
                                   self.hex_pos,
                                   self.tail_pos,
                                   self.sep_pos)

    def byte_coloring_positions(self, byte):
        bytes_per_row = self.bytes_per_row
        line = byte // bytes_per_row + 1
        pos_in_line = byte % bytes_per_row
    ##hex
        hex_start_col = self.hex_pos + pos_in_line * 3
        if pos_in_line >= bytes_per_row // 2:
            hex_start_col += len(self.separator)
        hex_end_col = hex_start_col + 2
    ##ascii
        ascii_start_col = self.tail_pos + pos_in_line

        return line, hex_start_col, hex_end_col, ascii_start_col

    def position_to_byte(self, row, col):
        bytes_per_row = self.bytes_per_row
        if bytes_per_row == 0:
            print('Немає байтів в рядку')
            return None
        
        row_bytes = (row - 1) * bytes_per_row

        if col >= self.tail_pos:
            # Достатньо відняти початок хвоста
            # Якщо ми занадто справа, перестрибуємо на останній байт
            col = min(col, self.tail_pos + bytes_per_row - 1)
            return row_bytes + col - self.tail_pos

        # Якщо ми занадто зліва, перестрибуємо на перший байт
        col = max(col, self.hex_pos)
        # Якщо ми занадто справа, перестрибуємо на останній байт
        col = min(col, self.tail_pos - 4)

        # Пропускаємо сепаратор
        if col > self.sep_pos:       
            col -= len(self.separator)
            col = max(col, self.sep_pos)

        return row_bytes + (col - self.hex_pos + 2) // 3
       
    def byte_to_tkinter_coords(self, byte, side):
        line, hex_start_col, hex_end_col, ascii_start_col = self.byte_coloring_positions(byte)
        if side == 1:
            b_hex_coords =  f'{line}.{hex_start_col}'
            return b_hex_coords
        else:
            b_ascii_coords = f'{line}.{ascii_start_col}'
            return b_ascii_coords

    def where_is_cursor(self, row, col):
        if col >= self.tail_pos - 1:
            return 2
        else:
            return 1
        
def init_formats():
    res = {} 
    winw = ( (400, 4), (700, 8), (1000, 16), (1300, 24), (1600, 32) )
    for key, bytes_per_row in winw:
        res[key] = HexFormat(key, bytes_per_row)
    return res

formats = init_formats()

def get_hex_format(winw):
        fmt_key = sorted(formats.keys())
        for maxw in fmt_key:
            if winw < maxw:
               return formats[maxw]
        else:
            return formats[fmt_key[-1]]

def hex_print(data, winW):
        res = ''
        bts = 0
        fmts = get_hex_format(winW)
        bts = fmts.bytes_per_row

        addr = 0
        while addr < len(data):
            tail = len(data) - addr
            index = tail if tail < len(fmts.formats) else -1
            fmt_head, fmt_tail = fmts.formats[index]
            line = ''.join([
                fmt_head.format(addr, *data[addr:addr+bts], *[ 0 ]*32),
                fmt_tail.format(*list(map(one_byte_to_ascii, data[addr:addr+bts])), *[ 0 ]*32)
                ])
            
            sep_index = 10+3*bts//2
            
            line = line[:sep_index] + fmts.separator + line[sep_index:]
            
            res += line + '\n'
            addr += bts
       
        return res

def tmp(fmt, byt):
    print(test_many_positions(fmt.line_len + 3, *fmt.byte_coloring_positions(byt)[1:]))

if __name__ == "__main__":
    # print(f'{bcolors.OKGREEN}Hello{bcolors.OKBLUE} Vlad{bcolors.ENDC}!')

    winW = 240
    print(hex_print([ ord(c) for c in 'al;weoiurya,kjsdhvfauuweyrdfgfdgdfhdjfgjfyhhhu' ] + [ 0, 5, 8 ], winW))
    cur_format = get_hex_format(winW)
#    print(cur_format.test_positions())
#    print(cur_format.byte_coloring_positions(3)[1:])
    for i in range(10):
        # tmp(cur_format, i)
        print(cur_format.byte_to_tkinter_coords(i))
