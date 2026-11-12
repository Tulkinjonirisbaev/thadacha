# Собирает лендинг из index.src.html:
#   index.html — русская версия, uz.html — узбекская (перевод в i18n_uz.py).
# SVG из brand/ встраиваются прямо в страницу.
import re, base64, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from i18n_uz import TEXT, RAW

CYR = re.compile(r'[А-Яа-яЁё]')

def inline_svg(s):
    def rep(m):
        b = base64.b64encode(open(m.group(2), 'rb').read()).decode()
        return f'{m.group(1)}="data:image/svg+xml;base64,{b}"'
    return re.sub(r'(src|href)="(brand/[\w-]+\.svg)"', rep, s)

# Алфавит по закону ЗРУ-1184 от 21.10.2026: oʻ→ö, gʻ→ğ, sh→ş, ch→ç. Название продукта не трогаем.
def new_alpha(t):
    t = t.replace('Thadacha', '\0')
    for a, b in (('O\u02bb', 'Ö'), ('o\u02bb', 'ö'), ('G\u02bb', 'Ğ'), ('g\u02bb', 'ğ')):
        t = t.replace(a, b)
    t = re.sub(r'S[hH]', 'Ş', t).replace('sh', 'ş')
    t = re.sub(r'C[hH]', 'Ç', t).replace('ch', 'ç')
    return t.replace('\0', 'Thadacha')

def to_uz(s):
    a, b = s.index('<body>'), s.index('<script>')
    missing = []
    def node(m):
        raw = m.group(1); key = raw.strip()
        if key not in TEXT:
            missing.append(key); return m.group(0)
        return '>' + raw.replace(key, new_alpha(TEXT[key])) + '<'
    body = re.sub(r'>([^<>]*[А-Яа-яЁё][^<>]*)<', node, s[a:b])
    s = s[:a] + body + s[b:]
    for ru, uz in RAW:
        if ru not in s: missing.append(ru)
        s = s.replace(ru, new_alpha(uz))
    # tutuq belgisi: в Nunito нет U+02BC — ставим типографский апостроф, который есть в обоих шрифтах
    s = s.replace('\u02bb', '\u2018').replace('\u02bc', '\u2019')
    s = s.replace('<html lang="ru">', '<html lang="uz">')
    s = s.replace('<link rel="canonical" href="https://thadacha.uz/">', '<link rel="canonical" href="https://thadacha.uz/uz.html">')
    s = s.replace('<a href="index.html" aria-current="true">RU</a><a href="uz.html">UZ</a>',
                  '<a href="index.html">RU</a><a href="uz.html" aria-current="true">UZ</a>')
    # что осталось кириллицей вне комментариев — не переведено
    plain = re.sub(r'<!--.*?-->|/\*.*?\*/|^\s*//.*$', '', s, flags=re.S | re.M)
    missing += sorted(set(re.findall(r'[^<>"\'\n]*[А-Яа-яЁё][^<>"\'\n]*', plain)))
    if missing:
        sys.exit('Нет перевода для:\n  ' + '\n  '.join(dict.fromkeys(missing)))
    return s

src = open('index.src.html').read()
open('index.html', 'w').write(inline_svg(src))
open('uz.html', 'w').write(inline_svg(to_uz(src)))
print('index.html и uz.html готовы')
