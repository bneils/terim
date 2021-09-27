#!/usr/bin/env python3
import argparse
import curses
import itertools
import os
import time

from PIL import Image

def gif_walk(gif):
    frames = []
    gif.seek(1)
    try:
        while True:
            gif.seek(len(frames))
            frames.append(gif.copy())
    except EOFError:
        return frames

def display_images(scr, images):
    """Curses function that resizes and displays an image inside a terminal"""
    assert curses.can_change_color() and curses.has_colors()
    curses.start_color()
    scr.nodelay(True)
    curses.noecho()
    last_size = None
    
    for frame in itertools.cycle(images):
        height, width = scr.getmaxyx()
        wait = frame.info.get("duration") or 1000//30
        
        # Size changed or screen initialized
        if (height, width) != last_size or len(images) > 1:
            start = time.time()
            last_size = (height, width)
            resized_image = frame.resize((width, height)).convert("P", palette=Image.ADAPTIVE, colors=curses.COLORS - 1)
            # Create curses color palette
            palette = resized_image.getpalette()
            palette = [palette[i:i + 3] for i in range(0, 3 * (curses.COLORS - 1), 3)]
            for i, color in enumerate(palette):
                n = i + 1
                rgb1000 = [ int(c / 255 * 1000) for c in color ] 
                curses.init_color(n, *rgb1000)
                curses.init_pair(n, 0, n)
            # Write to screen
            scr.erase()
            data = list(resized_image.getdata())
            last = data.pop(-1)
            for i in data:
                scr.addch(" ", curses.color_pair(i + 1))
            # Insert at bottom right to not move cursor and cause ERR
            scr.insch(height - 1, width - 1, " ", curses.color_pair(last + 1))
            scr.refresh()
            end = time.time()
            elapsed = int(1000 * (end - start))
            wait -= elapsed
        if scr.getch() == ord("q"):
            break
        curses.napms(wait)

def main():
    parser = argparse.ArgumentParser(description="display images in the terminal.")
    parser.add_argument("input", metavar="fp", help="file path to image.")
    args = parser.parse_args()

    image = Image.open(args.input)
    if "loop" in image.info:
        curses.wrapper(display_images, gif_walk(image)) # GIF
    else:
        curses.wrapper(display_images, [image])

if __name__ == "__main__":
    main()
