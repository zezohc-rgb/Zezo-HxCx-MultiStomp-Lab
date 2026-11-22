"""128x64 monochrome CE-2 cover in the compact pedal style of Zoom's BF-2.

Original pixel drawing, not an extracted stock BF-2 bitmap. Knob value
overlays are drawn by the firmware at (26,46) and (82,46).
"""
from screen_image import Canvas, encode_zoom_rle


def make_ce2_screen():
    c = Canvas()
    # Compact stompbox silhouette in the upper band.
    c.rect(25, 2, 102, 39)
    c.rect(27, 4, 100, 37)
    # Two small top-mounted controls, like a compact two-knob pedal.
    for x in (43, 84):
        c.circle(x, 10, 5)
        c.vline(x, 6, 9)
        c.px(x, 10)
    # CE-2 model lettering centered and legible on monochrome LCD.
    c.draw_text("CE-2", 41, 19, scale=3, spacing=2)
    c.hline(35, 92, 35)
    # Two live value boxes will overlay these dial positions.
    c.draw_text("RATE", 26, 40)
    c.draw_text("DEPTH", 82, 40)
    # Do not draw behind the firmware's value rectangles (y=46..61).
    return encode_zoom_rle(c)
