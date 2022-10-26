# Misc utilities

def remove_multiple_chars(str, chars):
        for c in chars:
            str = str.replace(c, '')
        return str