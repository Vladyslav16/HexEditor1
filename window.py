from pprint import pprint
from tkinter import EventType
### !Конфігурації для різних елементів GUI! ###
MenuConfig = {
    'font': ("Times New Roman", 12, "bold"),
    'bg': "lightgray",
    'fg': "black",
    'activebackground': "lightblue",
    'activeforeground': "gray",
    'tearoff': 0 # Вимикає відокремлення меню
}
ButtonConfig = {
    'font': ("Times New Roman", 12, "bold"),
    'bg': "lightgray",
    'fg': "black",
    'activebackground': "lightblue",
    'activeforeground': "gray"
}

EntryConfig = {
    'font': ("Times New Roman", 12),
    'bg': "white",
    'fg': "black",
    'highlightbackground': "gray",
    'highlightthickness': 1
}

LabelConfig = {
    'font': ("Times New Roman", 12),
    'bg': "lightgray",
    'fg': "black"
}
### ^Конфігурації для різних елементів GUI^ ###


def tkinter_to_turtle(x_tkinter, y_tkinter, width, height):
    """
    Переводить координати tkinter ---> turtle
    """
    xt0 = width // 2
    yt0 = height // 2
    return x_tkinter - xt0, -(y_tkinter - yt0)


def turtle_to_tkinter(x_turtle, y_turtle, width, height):
    """
    Переводить координати turtle ---> tkinter
    """
    xt0 = width // 2
    yt0 = height // 2
    return x_turtle + xt0, yt0 + y_turtle


def win_to_center(parent, window_width, window_height):
    """
    Центрує вікно на екрані.
    """
    parent.update_idletasks()
    x = (parent.winfo_screenwidth() - window_width) // 2
    y = (parent.winfo_screenheight() - window_height) // 2 - 20
    parent.geometry(f"{window_width}x{window_height}+{x}+{y}")
##    parent.resizable(False, False)

##    parent.wm_attributes("-topmost", 1)

def indent(string, width, space = ' '):
    """
        Відступ в тексті
    """
    if len(string) >= width:
        return string
    else:
        return string + '\t'
#        return string + (space * (width - len(string)))

def switch_window(current_master, next_window):
    """
    Функція для перемикання між вікнами.()
    """
    # Очищення всіх елементів з поточного контейнера
    for widget in current_master.winfo_children():
        widget.destroy()

    # Ініціалізація нового вікна
    next_window = next_window(current_master)
    next_window.grid(row=0, column=0, sticky="nsew")

class TextMatrix:
    def __init__(self, event, sps = ' '):
        self.masks = {
            0x0001: "Shift",
            0x0002: "CapsLock",
            0x0004: "Ctrl",
            0x0008: "Alt",
            0x0010: "NumLock",
            0x0080: "RightAlt",
            0x0100: "Mouse1",
            0x0200: "Mouse2",
            0x0400: "Mouse3",
        }
        self.data = vars(event)
        self.state = event.state
        self.binary = f"{self.state:032b}"
        self.bits = list(self.binary)

        rows = max(len(keyword) for keyword in self.masks.values())
        cols = len(self.bits)

        self.field = self._prepare_field(rows, cols, sps)
        self.rows = rows
        self.cols = cols
        self.sps  = sps

        for col, bit in enumerate(self.bits[:self.cols]):
            self.field[0][col] = bit

    def _prepare_field(self, rows, cols, sps):
        res = []
        for r in range(rows):
            res.append([sps]*cols)
        return res
    
    def vertical_print(self, overwrite = True):
        for mask, text in self.masks.items():
            if self.state & mask:
                bit_index = mask.bit_length()
                column = self.cols - bit_index
             
                tail = self.sps * self.rows if overwrite else ''
                for row, char in enumerate((text + tail)[:self.rows - 1]):
                    self.field[row + 1][column] = char

    def _field_to_text(self, filler):
        return [ filler.join(row) for row in self.field ]

    def print(self, filler = ''):
        for row in self._field_to_text(filler): print(row)



##def print_event(event):
##    """
##    Print tkinter event + event.state
##    """
##    data = vars(event)
##    state = event.state
##    
##    masks = {
##        0x0001: "Shift",
##        0x0002: "CapsLock",
##        0x0004: "Ctrl",
##        0x0008: "Alt",
##        0x0010: "NumLock",
##        0x0080: "RightAlt",
##        0x0100: "Mouse1",
##        0x0200: "Mouse2",
##        0x0400: "Mouse3",
##    }
##    
##    res = {}
##    
##    for mask, name in masks.items():
##        res[name] = {
##            "mask_decimal": mask,
##            "mask_binary": f"{mask:016b}",
##            "active": bool(state & mask),
##        }
##        
##    print("\n" + "*" * 80)
##    print("EVENT")
##    if event.type == EventType.KeyRelease:
##        print("key released")
##    else:
##        print("key pressed")
##    print("*" * 80)
##    pprint(data, sort_dicts=False, width=1)
##
##    print("\n" + "-" * 80)
##    print("COMBINATION")
##    print("-" * 80)
##    combination = [name for mask, name in masks.items() if state & mask]
##    pprint(combination if combination else ["None"])
##
##    print("\n" + "-" * 80)
##    print("STATE")
##    print("-" * 80)
##    print(f"decimal : {state}")
##    print(f"binary:")
##    
##    binary = f"{state:016b}"
##    bits = list(binary)
##    
##    print(f"{'index:':<6} " + " ".join(f"{i+1:<2}" for i, _ in enumerate(bits)))
##    print(f"{'bits:':<6} " + " ".join(f"{bit:<2}" for _, bit in enumerate(bits)))
##
##    for i, bit in enumerate(bits):
##        if bit == '1':
##            print(f"active bit: {i}")
##    
##    for mask, name in masks.items():
##        if state & mask:    
##            print("\n".join(" " * 7 + c for c in name))
##    
####    pprint(res, sort_dicts=False, width=1)
##    print("-" * 80)
