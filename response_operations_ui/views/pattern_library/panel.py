# Panel macro component
# As found in pattern library


def panel(*args, **kwargs):
    panel_class = 'panel' if 'class' not in kwargs else 'panel ' + kwargs['class']
    header = None if 'header' not in kwargs else kwargs['header']
    font_size = 'venus' if 'font_size' not in kwargs else kwargs['font_size']
    id = None if 'id' not in kwargs else kwargs['id']
    body = args

    header_markup = _header_markup(header, font_size)

    markup = f'''
    <div class="{panel_class}">
        {header_markup}
        <div id="{id}" class="panel__body">
            {body}
        </div>
    </div>'''
    return markup


def _header_markup(header, font_size):
    if header:    
        return f'''
        <div class="panel__header>
            <div class="{font_size}">{header}</div>
        </div>'''
    else:
        return ''
