#! /usr/bin/env python
# -*- encoding: utf-8 -*-


from django.forms import widgets
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape, escape
from itertools import chain
from django.utils.safestring import mark_safe
from django.conf import settings

def make_css_style(valor):
    '''
    Crear el CSS para la lista de colores.
    '''
    fore = ''
    # Sacar los valores
    r,g,b = valor[:2], valor[2:4], valor[4:]
    r, g, b = map(lambda x: int(x, 16) + 1, (r, g, b))
    # print r, g, b
    if (r + g + b) / 3.0 < 128:
        fore = '#ffffff'
    return 'background-color: #%s; color: %s' % (valor, fore)


class ColorSelect(widgets.Select):
    
    def render_options(self, choices, selected_choices):
        def render_option(option_value, option_label):
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
            return u'<option value="%s"%s style="%s">%s</option>' % (
                escape(option_value), selected_html,
                make_css_style(option_value),
                conditional_escape(force_unicode(option_label)))
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(render_option(*option))
                output.append(u'</optgroup>')
            else:
                output.append(render_option(option_value, option_label))
        return u'\n'.join(output)
    
class CuatrimestreDateWidget(widgets.DateTimeInput):
    def __init__(self, *largs, **kwargs):
        kwargs.update(
                      attrs = {'class' : 'vDateField CutrimestreField', 'size':10},
                      format = settings.DATETIME_FORMAT
                      )
        super(CuatrimestreDateWidget, self).__init__(*largs, **kwargs)

    def render(self, name, value, attrs=None):
        s = widgets.DateTimeInput.render(self, name, value, attrs)
        return mark_safe(s)
