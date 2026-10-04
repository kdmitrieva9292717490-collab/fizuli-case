"""Генератор: данные текстовых блоков из Figma -> HTML с абсолютными координатами.
Использование: python tools/gen.py  (читает JSON выгрузки и вставляет блоки в index.html)"""
import json, html, re, sys

SHOTS = 'C:/Users/79292/AppData/Local/Temp/claude/shots/'
RENDER = {  # границы букв Supermolot (x, y) в блоке — для точной позиции SVG
    '2130:23361': (52.68, 712.4), '2130:23364': (402.78, 713), '2130:23367': (728.6, 713), '2130:23370': (1056.1, 712.4),
    '2144:16409': (50.4, 178), '2144:16417': (726.6, 178),
}


def rgba(hexc, o):
    r, g, b = int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)
    return f'rgb({r},{g},{b})' if o >= 0.999 else f'rgba({r},{g},{b},{o})'


def text_div(i, svg):
    if i.get('sup'):
        s = svg[i['id']]
        x, y = i.get('rb') or RENDER[i['id']]
        return f'<img class="t" src="{s["file"]}" alt="{html.escape(i["s"])}" style="left:{x}px;top:{y}px;width:{s["w"]}px;height:{s["h"]}px">'
    st = [f'left:{i["x"]}px', f'top:{i["y"]}px', f'font-size:{i["fs"]}px', f'color:{rgba(i["c"], i["o"])}']
    if i['st'] == 'Bold':
        st.append('font-weight:700')
    lh = i['lh']
    if lh is None:
        lines = max(1, round(i['h'] / (i['fs'] * 1.2)))
        st.append(f'line-height:{round(i["h"] / lines, 2)}px')
    elif isinstance(lh, str):
        st.append(f'line-height:{lh}')
    else:
        st.append(f'line-height:{round(lh, 3)}')
    if i['ls']:
        st.append(f'letter-spacing:{i["ls"]}')
    st.append(f'width:{i["w"]}px')
    if i['ar'] == 'WIDTH_AND_HEIGHT':
        st.append('white-space:nowrap')
    if i['al'] != 'LEFT':
        st.append(f'text-align:{i["al"].lower()}')
    txt = html.escape(i['s']).replace('\n', '<br>')
    return f'<div class="t" style="{";".join(st)}">{txt}</div>'


def rect_div(i):
    st = [f'left:{i["x"]}px', f'top:{i["y"]}px', f'width:{i["w"]}px', f'height:{i["h"]}px']
    if 'c' in i:
        st.append(f'background:{rgba(i["c"], i["o"])}')
    return f'<div class="r" style="{";".join(st)}"></div>'


def build(block, svg):
    out = [text_div(i, svg) if i['t'] == 'T' else rect_div(i) for i in block['items']]
    return '\n        '.join(out)


if __name__ == '__main__':
    data = json.load(open(SHOTS + 'blocks25.json', encoding='utf-8'))
    svg = json.load(open(SHOTS + 'svginfo.json', encoding='utf-8'))
    s = open('index.html', encoding='utf-8').read()
    for key, alt, label, extra in (('b2', '02 · Бренд и задача', '02 · Бренд и задача', 'b2'), ('b5', 'Структура сайта', '05 · Структура', 'b5'), ('b6', 'Цвет и типографика', '06 · Цвет и типографика', 'b6')):
        b = data[key]
        sec = f'''<section class="block" aria-label="{label}">
      <div class="stage tb {extra}" style="height:{b['h']}px;background:{b['bg']}">
        {build(b, svg)}
      </div>
    </section>'''
        m = re.search(r'<section class="block"[^>]*>\s*<img src="assets/images/[^"]*" alt="' + re.escape(alt) + r'"[^>]*>\s*</section>', s)
        if not m:
            print('не найден блок', key)
            continue
        s = s[:m.start()] + sec + s[m.end():]
        print('заменён', key, len(b['items']), 'элементов')
    open('index.html', 'w', encoding='utf-8', newline='').write(s)
