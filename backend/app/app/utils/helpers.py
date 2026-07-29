from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.util import ClassNotFound


def detect_language(filename: str, content: str) -> str:
    try:
        lexer = get_lexer_for_filename(filename)
        return lexer.name
    except ClassNotFound:
        try:
            lexer = guess_lexer(content)
            return lexer.name
        except ClassNotFound:
            return "Unknown"
