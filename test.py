def chunks(data, n):
    return [data[i:i+n] for i in range(0, len(data), n)]

def one_byte_to_ascii(b):
    return chr(b) if 0x1F < b < 0x80 else '.'

def bytes_to_ascii(data):
    return ''.join(one_byte_to_ascii(b) for b in data)

data = list(range(0x61, 0x81))

formats = {
    400: [4, [ ['', ''] ] + [
            ['{:08X}: ' + '{:02X} '*i + '   '*(4-i) + '| ', '{}'*i] for i in range(1, 5)
            ]
            ],

    700: [8, [ ['', ''] ] + [
            ['{:08X}: ' + '{:02X} '*i + '   '*(8-i) + '| ', '{}'*i] for i in range(1, 9)
            ]
            ],

    1000: [16, [ ['', ''] ] + [
            ['{:08X}: ' + '{:02X} '*i + '   '*(16-i) + '| ', '{}'*i] for i in range(1, 17)
            ]
            ],

    1300: [24, [ ['', ''] ] + [
            ['{:08X}: ' + '{:02X} '*i + '   '*(24-i) + '| ', '{:c}'*i] for i in range(1, 25)
            ]
            ],

    1600: [32, [ ['', ''] ] + [
            ['{:08X}: ' + '{:02X} '*i + '   '*(24-i) + '| ', '{:c}'*i] for i in range(1, 33)
            ]
            ],
    }


def hex_print(data, winW):
        res = ''
        bts = 0
        fmts = []
        fmt_key = sorted(formats.keys())
        for maxw in sorted(formats.keys()):
            if winW < maxw:
               bts, fmts = formats[maxw]
               break
        else:
            bts, fmts = formats[fmt_key[-1]]

        addr = 0
        while addr < len(data):
            tail = len(data) - addr
            index = tail if tail < len(fmts) else -1
            fmt_head, fmt_tail = fmts[index]
            res += fmt_head.format(addr, *data[addr:], *[ 0 ]*32)
            res += fmt_tail.format(*data[addr:], *[ 0 ]*32)
            res += '\n'
            addr += bts

        return res

if __name__ == "__main__":
    print(hex_print(data, 1200))

