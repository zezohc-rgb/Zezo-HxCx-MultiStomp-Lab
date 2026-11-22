"""Monochrome CE-2 pedal face for the 128×64 Zoom LCD."""

from screen_image import Canvas, encode_zoom_rle


def make_ce2_screen():
    c = Canvas()
    # Rounded shoulders, enclosure and footswitch hinge.
    c.hline(19, 108, 3)
    c.hline(14, 113, 6)
    for x in (12, 115):
        c.vline(x, 9, 39)
    c.hline(9, 118, 40)
    for x in (8, 119):
        c.vline(x, 40, 63)
    c.hline(8, 119, 63)
    c.hline(15, 112, 60)

    for x, label, label_x in ((36, "RATE", 21), (92, "DEPTH", 73)):
        c.circle(x, 17, 11)
        c.filled_circle(x, 17, 9)
        c.vline(x - 1, 10, 17, 0)
        c.vline(x, 10, 17, 0)
        c.px(x - 15, 17)
        c.px(x + 15, 17)
        c.draw_text(label, label_x, 29, scale=2, spacing=2)

    c.rect(61, 10, 66, 15)
    c.rect(63, 12, 64, 13)
    c.draw_text("CE-2", 56, 20)
    c.draw_text("CHORUS", 52, 53)
    # Value overlays start at (26,46) and (82,46), each 20×15.
    # The bottom enclosure line at y=60 is broken across both overlays.
    c.hline(26, 45, 60, 0)
    c.hline(82, 101, 60, 0)
    return encode_zoom_rle(c)
