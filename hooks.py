import re
from html.parser import HTMLParser

# Matches the exact shape every page in this repo writes those two sections
# in: an <h2> with this id, followed directly by a single <ul>.
_SEE_ALSO_RE = re.compile(r'<h2 id="see-also".*?</h2>\s*<ul>.*?</ul>', re.S)
_FURTHER_READING_RE = re.compile(
    r'<h2 id="further-reading".*?</h2>\s*<ul>.*?</ul>', re.S
)


class _ListLinkExtractor(HTMLParser):
    """Pulls the heading text and every <a> inside the <ul> out of a
    fragment shaped like '<h2>Title</h2><ul><li><a href=..>Text</a> — more
    prose</li>...</ul>', dropping the prose. Used to rebuild the section as
    a plain link list styled like the TOC nav, rather than copying the
    article's own <h2>/<ul> (which carries duplicate ids and descriptions
    that don't fit a nav rail)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.links = []
        self._in_title = False
        self._in_li = False
        self._in_a = False
        self._href = None
        self._buf = []

    def handle_starttag(self, tag, attrs):
        if tag == "h2" and not self.title:
            self._in_title = True
        elif tag == "a" and self._in_title:
            # the heading's own permalink anchor, if any - not part of the title
            self._in_title = False
        elif tag == "li":
            self._in_li = True
        elif tag == "a" and self._in_li and not self._in_a:
            self._in_a = True
            self._href = dict(attrs).get("href", "#")
            self._buf = []
        elif self._in_a:
            self._buf.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == "h2":
            self._in_title = False
        elif tag == "a" and self._in_a:
            self._in_a = False
            self.links.append((self._href, "".join(self._buf)))
        elif tag == "li":
            self._in_li = False
        elif self._in_a:
            self._buf.append("</%s>" % tag)

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._in_a:
            self._buf.append(data)


def _as_nav(fragment, fallback_title):
    """Render an extracted section as a `.md-nav--secondary` block, the
    same structure partials/toc.html uses, so it picks up the real TOC's
    CSS instead of a hand-rolled lookalike."""
    if not fragment:
        return None
    parser = _ListLinkExtractor()
    parser.feed(fragment)
    if not parser.links:
        return None
    title = parser.title or fallback_title
    items = "".join(
        '<li class="md-nav__item">'
        '<a href="%s" class="md-nav__link"><span class="md-ellipsis">%s</span></a>'
        "</li>" % (href, label)
        for href, label in parser.links
    )
    return (
        '<nav class="md-nav md-nav--secondary" aria-label="%s">'
        '<label class="md-nav__title">%s</label>'
        '<ul class="md-nav__list">%s</ul>'
        "</nav>" % (title, title, items)
    )


def on_page_content(html, page, config, files, **kwargs):
    """Mirror 'See also' / 'Further reading' into a right-hand sidebar (see
    overrides/main.html) as plain nav links, matching the look of the TOC
    (which stays in the left nav via toc.integrate). `html` is returned
    unchanged — the in-body copies stay put and extra.css hides them once
    the right rail has room to show them."""
    see_also = _SEE_ALSO_RE.search(html)
    further_reading = _FURTHER_READING_RE.search(html)
    page.see_also_html = _as_nav(see_also.group(0) if see_also else None, "See also")
    page.further_reading_html = _as_nav(
        further_reading.group(0) if further_reading else None, "Further reading"
    )
    return html
