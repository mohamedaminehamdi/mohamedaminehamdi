"""Turns assets/me-blue.jpg into the ASCII portraits drawn on the profile card.

Run locally:    pip install pillow && python3 scripts/build_ascii.py && python3 scripts/update_card.py
Tune BOX to re-crop, GAMMA to lift or deepen the shadows (lower = brighter hair on the dark card).
"""
import os
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 60, 37                      # glyph grid; the card draws 7.2 x 14 px cells, so the crop is about 1 : 1.2
BOX = (410, 425, 790, 881)         # head, beard and a hint of collar, in source-photo pixels
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"   # light -> dense
GAMMA, EQUALISE = 0.6, 0.2         # shadow lift; share of rank-equalised tone mixed in for facial detail


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def portraits():
    crop = Image.open(os.path.join(ROOT, 'assets', 'me-blue.jpg')).convert('RGB').crop(BOX)
    small = crop.resize((W, H), Image.BOX)
    # subject = anything unlike the warm, dark backdrop (bluish suit, bright skin and shirt, hair); filled per row
    mask = []
    for y in range(H):
        row = [small.getpixel((x, y)) for x in range(W)]
        xs = [x for x, p in enumerate(row) if p[2] - p[0] > 9 or lum(p) > 62 or lum(p) < 20]
        mask.append([bool(xs) and xs[0] <= x <= xs[-1] for x in range(W)])
    tones = crop.convert('L').filter(ImageFilter.GaussianBlur(1.5)).filter(ImageFilter.UnsharpMask(8, 150, 1)).resize((W, H), Image.BOX)
    cells = sorted(((y, x) for y in range(H) for x in range(W) if mask[y][x]), key=lambda c: tones.getpixel((c[1], c[0])))
    rank = {c: i / (len(cells) - 1) for i, c in enumerate(cells)}
    vals = [tones.getpixel((x, y)) for y, x in cells]
    lo, hi = vals[int(len(vals) * 0.02)], vals[int(len(vals) * 0.99)]

    def tone(y, x):
        linear = min(1, max(0, (tones.getpixel((x, y)) - lo) / (hi - lo))) ** GAMMA
        return (1 - EQUALISE) * linear + EQUALISE * rank[(y, x)]

    # dark card: bright = dense; light card: dark = dense. The backdrop stays blank in both.
    return {theme: '\n'.join(''.join(RAMP[round((1 - tone(y, x) if invert else tone(y, x)) * (len(RAMP) - 1))] if mask[y][x] else ' '
                                     for x in range(W)).rstrip() for y in range(H))
            for theme, invert in (('dark', False), ('light', True))}


if __name__ == '__main__':
    for theme, art in portraits().items():
        with open(os.path.join(ROOT, 'scripts', f'ascii_{theme}.txt'), 'w') as f:
            f.write(art + '\n')
    print('wrote scripts/ascii_dark.txt and scripts/ascii_light.txt')
