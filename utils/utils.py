import re


def color_text(s, fg, bg, bold=True):
    format = ';'.join([str(int(bold)), str(fg), str(bg)])
    return f'\x1b[{format}m{s}\x1b[0m'


def print_qr_code(img):
    black_token = color_text("  ", 37, 40)
    white_token = color_text("  ", 30, 47)
    img = img.resize((540, 540))
    uw = 12
    icnt = 38
    width, _ = img.size
    pad = (width - uw * icnt) // 2
    result = ''
    for i in range(icnt):
        result += white_token
        for j in range(icnt):
            x_axis, y_axis = pad + uw * j, pad + uw * i
            b = img.getpixel((x_axis + uw // 2, y_axis + uw // 2))[0] < 128
            if b:
                result += black_token
            else:
                result += white_token
        result += white_token + '\n'
    whiterow = white_token * (icnt + 2)
    print(whiterow + '\n' + result + whiterow)


def remove_emoji(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+",
        flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)
