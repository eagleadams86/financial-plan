#!/usr/bin/env python3
"""Draw favicon.ico — the same mark as the inline SVG icon in index.html.

The app's icon is an inline SVG data URI, which every current browser prefers.
favicon.ico is the fallback: it's what a browser fetches from the site root on
its own, what older ones use, and what a bookmark or a search result shows. The
two have to be the same picture, so this draws the SVG's geometry with Pillow
rather than hand-editing a binary nobody can review in a diff.

    python3 make_favicon.py

Everything is drawn at 8x and reduced with Lanczos, which is what gives the
16px version clean edges. Keep the shapes here in step with the SVG in
index.html if that ever changes.
"""

from PIL import Image, ImageDraw

# The mark, in the SVG's own 64x64 coordinates.
BG = (10, 14, 26, 255)          # #0a0e1a — midnight, the default theme's page
GLOW = (20, 28, 51, 255)        # #141c33 — the darker disc in the corner
GRAD_FROM = (129, 140, 248)     # #818cf8 — midnight's accent
GRAD_TO = (165, 180, 252)       # #a5b4fc
LINE = [(11, 47), (24, 34), (34, 41), (53, 17)]   # the plan climbing
GRAD_AXIS = ((10, 52), (54, 12))                  # where the gradient runs
MARKER = (53, 17)               # the map pin at the end of the line

SCALE = 8                       # supersample, then reduce
SIZES = [16, 32, 48, 64, 128, 256]


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def gradient_at(point):
    """Colour for a point, projected onto the gradient's axis."""
    (x0, y0), (x1, y1) = GRAD_AXIS
    dx, dy = x1 - x0, y1 - y0
    span = dx * dx + dy * dy
    t = ((point[0] - x0) * dx + (point[1] - y0) * dy) / span
    return lerp(GRAD_FROM, GRAD_TO, min(1.0, max(0.0, t)))


def draw_gradient_line(d, pts, width):
    """A gradient stroke, drawn as short segments each of one colour.

    Round joins come from stamping a circle at every step: a polyline drawn in
    pieces would otherwise show a notch at each corner.
    """
    steps = 400
    flat = []
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        for s in range(steps):
            t = s / steps
            flat.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    flat.append(pts[-1])
    r = width / 2
    for x, y in flat:
        d.ellipse([(x - r) * SCALE, (y - r) * SCALE,
                   (x + r) * SCALE, (y + r) * SCALE],
                  fill=gradient_at((x, y)) + (255,))


def build():
    n = 64 * SCALE
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, n, n], fill=BG)
    # the soft disc bottom-left, the way the SVG has it
    d.ellipse([(14 - 20) * SCALE, (52 - 20) * SCALE,
               (14 + 20) * SCALE, (52 + 20) * SCALE], fill=GLOW)
    draw_gradient_line(d, LINE, 5)
    mx, my = MARKER
    d.ellipse([(mx - 6.5) * SCALE, (my - 6.5) * SCALE,
               (mx + 6.5) * SCALE, (my + 6.5) * SCALE], fill=GRAD_TO + (255,))
    d.ellipse([(mx - 2.4) * SCALE, (my - 2.4) * SCALE,
               (mx + 2.4) * SCALE, (my + 2.4) * SCALE], fill=BG)

    # Round the corners with an alpha mask. The SVG leaves the disc square at
    # the edges; an icon reads better rounded, and this is the file that ends
    # up on a bookmarks bar.
    mask = Image.new('L', (n, n), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, n - 1, n - 1],
                                           radius=14 * SCALE, fill=255)
    img.putalpha(mask)
    return img


def main():
    art = build()
    frames = [art.resize((s, s), Image.LANCZOS) for s in SIZES]
    frames[-1].save('favicon.ico', format='ICO',
                    sizes=[(s, s) for s in SIZES])
    print('favicon.ico written at ' + ', '.join(f'{s}px' for s in SIZES))
    print('Now bump the ?v= on every favicon.ico reference — both in index.html '
          'and the one in privacy.html — browsers cache an icon for a long time '
          'and will keep showing the old one otherwise.')


if __name__ == '__main__':
    main()
