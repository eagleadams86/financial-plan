#!/usr/bin/env python3
"""Draw favicon.ico and the install icons — the same mark as the inline SVG in
index.html.

The app's icon is an inline SVG data URI, which every current browser prefers.
favicon.ico is the fallback: it's what a browser fetches from the site root on
its own, what older ones use, and what a bookmark or a search result shows. The
install icons named by manifest.webmanifest are a third copy, because a manifest
icon must be a fetchable file and cannot be a data URI. All of them have to be
the same picture, so this draws the SVG's geometry with Pillow rather than
hand-editing binaries nobody can review in a diff.

    python3 make_favicon.py

Everything is drawn at 8x and reduced with Lanczos, which is what gives the
16px version clean edges. Keep the shapes here in step with the SVG in
index.html if that ever changes.

Three shapes come out of the one mark, and the differences are not decoration:

- **favicon.ico and the manifest's `any` icons are ROUNDED.** Nothing masks
  them, so the corners have to be in the file.
- **The `maskable` icon is a full-bleed square with the mark inset**, because
  the platform crops it to whatever shape it likes — a circle on some Android
  launchers. Anything in the corners is thrown away, so the mark is drawn at
  MASKABLE_SCALE and the background runs to the edges. Rounding it as well would
  round a picture that is about to be rounded again.
- **apple-touch-icon.png is SQUARE**, for the same reason in reverse: Apple
  applies its own corner radius, and a rounded source under that mask leaves a
  pale seam inside the curve.
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

# The install icons, named by manifest.webmanifest and by index.html's
# apple-touch-icon link. 192 and 512 are the two sizes Chrome asks for; 180 is
# Apple's. Renaming any of these means editing both files.
PWA_ICONS = [(192, 'icon-192.png'), (512, 'icon-512.png')]
MASKABLE = (512, 'icon-512-maskable.png')
APPLE = (180, 'apple-touch-icon.png')

# How much of a maskable icon the mark is allowed to fill. The safe zone is the
# centre circle of 80% diameter, so a square of side s has its own corners at
# s×√2/2 from the middle: at 0.55 that's 0.389 of the width, inside the 0.4
# radius with a little to spare. Bigger and the climbing line's ends start
# living in the part a circular mask cuts off.
MASKABLE_SCALE = 0.55


def lerp(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def scaled(point, k):
    """A point of the mark, moved towards the middle of the 64x64 box.

    Everything scales about the CENTRE — the line, the marker, the disc and the
    gradient's own axis — which is what keeps the inset maskable icon the same
    picture rather than a smaller copy pasted into a bigger square. The first
    attempt did paste, and the disc, which is drawn to bleed off the bottom-left
    corner, came back with the straight edges of the tile it was pasted from
    cut through it.
    """
    return (32 + (point[0] - 32) * k, 32 + (point[1] - 32) * k)


def gradient_at(point, axis):
    """Colour for a point, projected onto the gradient's axis."""
    (x0, y0), (x1, y1) = axis
    dx, dy = x1 - x0, y1 - y0
    span = dx * dx + dy * dy
    t = ((point[0] - x0) * dx + (point[1] - y0) * dy) / span
    return lerp(GRAD_FROM, GRAD_TO, min(1.0, max(0.0, t)))


def draw_gradient_line(d, pts, width, axis):
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
                  fill=gradient_at((x, y), axis) + (255,))


def disc(d, centre, radius, fill):
    (cx, cy), r = centre, radius
    d.ellipse([(cx - r) * SCALE, (cy - r) * SCALE,
               (cx + r) * SCALE, (cy + r) * SCALE], fill=fill)


def build(rounded=True, k=1.0):
    n = 64 * SCALE
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, n, n], fill=BG)
    # the soft disc bottom-left, the way the SVG has it
    disc(d, scaled((14, 52), k), 20 * k, GLOW)
    axis = tuple(scaled(p, k) for p in GRAD_AXIS)
    draw_gradient_line(d, [scaled(p, k) for p in LINE], 5 * k, axis)
    disc(d, scaled(MARKER, k), 6.5 * k, GRAD_TO + (255,))
    disc(d, scaled(MARKER, k), 2.4 * k, BG)

    # Round the corners with an alpha mask. The SVG leaves the disc square at
    # the edges; an icon reads better rounded, and this is the file that ends
    # up on a bookmarks bar. Skipped for the icons something else will mask —
    # see the note at the top of the file.
    if rounded:
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

    square = build(rounded=False)
    for size, name in PWA_ICONS:
        art.resize((size, size), Image.LANCZOS).save(name, format='PNG')
        print(f'{name} written')
    size, name = APPLE
    # No alpha channel: Apple asks for an opaque icon, and every pixel of this
    # one is opaque already — carrying the channel would only invite a renderer
    # to composite it against something.
    square.resize((size, size), Image.LANCZOS).convert('RGB').save(
        name, format='PNG')
    print(f'{name} written (square, opaque — Apple masks it)')
    size, name = MASKABLE
    build(rounded=False, k=MASKABLE_SCALE).resize(
        (size, size), Image.LANCZOS).save(name, format='PNG')
    print(f'{name} written (full bleed, mark at {MASKABLE_SCALE:.0%})')

    print('Now bump the ?v= on every favicon.ico reference — both in index.html '
          'and the one in privacy.html — browsers cache an icon for a long time '
          'and will keep showing the old one otherwise.')


if __name__ == '__main__':
    main()
