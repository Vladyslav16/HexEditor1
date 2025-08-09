'''
helpers
Допоміжні функції для роботи з байтами та позиціями в hex-редакторі.
'''
import tkinter as tk

def chunks(data, n):
    return [data[i:i+n] for i in range(0, len(data), n)]

def one_byte_to_ascii(b):
    return chr(b) if 0x1F < b < 0x80 else '.'

def bytes_to_ascii(data):
    return ''.join(one_byte_to_ascii(b) for b in data)

def cursor_position(editor_instance, event=None):
    editor_instance.ed_context.clear_highlight('insert')
    byte_number = editor_instance.ed_context.cursor_pos_to_byte_number()
    if byte_number is None:
        print('Can not edit here!')
        return "break"
    row, hex_pos, ascii_pos = editor_instance.ed_context.calc_cursor_position(byte_number)
    print(f'Byte: {byte_number} | Position: hex({row}, {hex_pos}), ascii({row}, {ascii_pos})')
    editor_instance.ed_context.highlight_byte(byte_number, 'insert')
