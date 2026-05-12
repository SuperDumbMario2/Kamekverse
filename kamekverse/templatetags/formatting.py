import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def formatting(value):
    lines = str(value).splitlines()
    linesarray = []
    for line in lines:
        escapedline = escape(line)
        if re.match(r"^&gt;", escapedline):
            linesarray.append(f'<span class="greentext">{escapedline}</span>')
        elif re.match(r"^&lt;", escapedline):
            linesarray.append(f'<span class="orangetext">{escapedline}</span>')
        elif re.match(r"^\^", escapedline):
            linesarray.append(f'<span class="bluetext">{escapedline}</span>')
        else:
            linesarray.append(escapedline)
    return mark_safe("<br>".join(linesarray))