from typing import Optional
from html_sanitizer import Sanitizer
import markdown2

_sanitizer = Sanitizer({"keep_typographic_whitespace": True, "tags": {
        "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
        "li", "br", "sub", "sup", "hr", "u"
    }})


def sanitize_html(html: Optional[str]) -> str:
    if html is None:
        return ""
    return _sanitizer.sanitize(markdown2.markdown(html))
