# Misc utiliy functions
class Utils:
    @staticmethod
    def remove_multiple_chars(str, chars):
        for c in chars:
            str = str.replace(c, '')
        return str