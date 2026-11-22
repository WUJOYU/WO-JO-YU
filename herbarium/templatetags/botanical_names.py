"""Display botanical names without changing stored nomenclatural data."""
import re
from django import template
from django.utils.html import format_html, format_html_join

register = template.Library()
RANKS = {'subsp.', 'ssp.', 'var.', 'subvar.', 'f.', 'forma', 'subf.'}
MARKERS = {'sp.', 'spp.', 'cf.', 'aff.', '×', 'x'}

@register.filter(name='botanical_name')
def botanical_name(value):
    """Italicize genus, specific and infraspecific epithets; keep authors and ranks roman.

    Conservative presentation parser: does not attempt nomenclatural validation.
    """
    words = str(value or '').split()
    if not words:
        return '—'
    rendered = []
    expect_epithet = False
    species_seen = False
    for i, word in enumerate(words):
        low = word.lower()
        italic = False
        if i == 0:
            italic = True
        elif low in RANKS:
            expect_epithet = True
        elif expect_epithet:
            italic = True
            expect_epithet = False
        elif not species_seen and i > 0 and low not in MARKERS and re.fullmatch(r'[a-z][a-z-]*', word):
            italic = True
            species_seen = True
        elif low in {'sp.', 'spp.'}:
            species_seen = True
        rendered.append(format_html('<i>{}</i>', word) if italic else format_html('{}', word))
    return format_html_join(' ', '{}', ((w,) for w in rendered))
