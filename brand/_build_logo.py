# Генератор логотипа Thadacha: знак + разделитель + леттеринг, без зависимостей от шрифтов.
BLUE, GREEN, AMBER, NAVY, GREY = "#0F5BFF", "#1DBF73", "#FFAB0A", "#0A1740", "#A9ADB8"
W = 26  # толщина штриха, x-высота 100, высота прописной 150

def mark(x=0, y=0, c=(BLUE, GREEN, AMBER)):
    rows = [(194, c[0]), (160, c[1]), (165, c[2])]
    return "".join(f'<rect x="{x}" y="{y + i*71}" width="{w}" height="54" rx="27" fill="{col}"/>'
                   for i, (w, col) in enumerate(rows))

def stem(x, top): return f'<rect x="{x}" y="{top}" width="{W}" height="{150-top}" rx="7"/>'
def bowl(x): return f'<circle cx="{x+50}" cy="100" r="37" fill="none" stroke-width="{W}"/>'
def T(x): return f'<rect x="{x}" y="0" width="104" height="{W}" rx="7"/>' + stem(x + 39, 0)
def h(x): return stem(x, 0) + f'<path d="M{x+13},104 A37,37 0 0 1 {x+87},104 V143" fill="none" stroke-width="{W}"/>' + f'<rect x="{x+74}" y="130" width="{W}" height="20" rx="7"/>'
def a(x): return bowl(x) + stem(x + 74, 50)
def d(x): return bowl(x) + stem(x + 74, 0)
def c(x): return f'<path d="M{x+78.3},76.2 A37,37 0 1 0 {x+78.3},123.8" fill="none" stroke-width="{W}" stroke-linecap="round"/>'

def word(x, y, ink):
    seq = [(T, 0), (h, 116), (a, 232), (d, 348), (a, 464), (c, 580), (h, 688), (a, 804)]
    return f'<g transform="translate({x},{y})" fill="{ink}" stroke="{ink}" stroke-width="0">' + "".join(f(o) for f, o in seq) + "</g>"

def svg(w, hgt, body, bg=None):
    r = f'<rect width="{w}" height="{hgt}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {hgt}" role="img" aria-label="Thadacha">{r}{body}</svg>\n'

def horizontal(ink, div, cols=(BLUE, GREEN, AMBER)):
    return mark(0, 0, cols) + f'<rect x="250" y="0" width="6" height="196" rx="3" fill="{div}"/>' + word(316, 23, ink)

out = {
 "logo-horizontal.svg": svg(1220, 196, horizontal(NAVY, GREY)),
 "logo-horizontal-dark.svg": svg(1220, 196, horizontal("#FFFFFF", "#3A4468")),
 "logo-mono-navy.svg": svg(1220, 196, horizontal(NAVY, NAVY, (NAVY,)*3)),
 "logo-mono-white.svg": svg(1220, 196, horizontal("#FFFFFF", "#FFFFFF", ("#FFFFFF",)*3)),
 "mark.svg": svg(194, 196, mark()),
 "wordmark.svg": svg(904, 150, word(0, 0, NAVY)),
 "app-icon.svg": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Thadacha"><rect width="512" height="512" rx="112" fill="{NAVY}"/><g transform="translate(111,109) scale(1.5)">{mark()}</g></svg>\n',
 "favicon.svg": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 194 196">{mark()}</svg>\n',
}
import os
here = os.path.dirname(os.path.abspath(__file__))
for n, s in out.items(): open(os.path.join(here, n), "w").write(s)
print("ok", list(out))
