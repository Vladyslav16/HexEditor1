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
