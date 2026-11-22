"""Pixel-art CE-2 cover, adapted from the approved concept for Zoom 128x64 LCD.

The 128x64 monochrome display has firmware-owned value overlays at
(26,46) and (82,46); keep those rectangles empty.
"""
from screen_image import Canvas, encode_zoom_rle

def make_ce2_screen():
    c = Canvas()
    # Stompbox outline, rounded shoulders and lower side hinges.
    c.hline(19,108,3); c.hline(14,113,6)
    c.vline(12,9,34); c.vline(115,9,34)
    c.hline(9,118,36)
    c.vline(8,36,63); c.vline(119,36,63)
    c.hline(8,119,63)
    for x in (9,10,117,118):
        c.vline(x,42,55)
    # Halftone shadow behind the knobs, restrained for real LCD.
    for y in range(8,29,3):
        for x in range(17,112,4):
            if (x+y)%7 < 3 and not (24<=x<=51 or 77<=x<=104):
                c.px(x,y)
    # Two large control knobs with white tick and concentric highlights.
    for x in (38,90):
        c.filled_circle(x,20,12)
        c.circle(x,20,13)
        c.vline(x-1,10,19,0); c.vline(x,10,19,0)
        c.hline(x-3,x+3,12,0)
        for dx,dy in ((-17,0),(17,0),(-12,-11),(12,-11)):
            c.px(x+dx,20+dy)
    # LED and model label. Bottom half imitates pedal switch plate.
    c.rect(62,11,67,16); c.rect(64,13,65,14)
    c.draw_text("RATE",25,33)
    c.draw_text("DEPTH",78,33)
    c.hline(15,112,40)
    c.draw_text("CE-2",44,42,scale=2,spacing=2)
    c.hline(15,112,61)
    # Small chorus designation above the firmware value area.
    c.draw_text("CHORUS",51,56)
    # Firmware will overlay value rectangles in the lower half.
    return encode_zoom_rle(c)
