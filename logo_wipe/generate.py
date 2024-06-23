#!/usr/bin/env python3

import numpy as np
from PIL import Image
import os
import random

#ROTATION=Image.ROTATE_90
ROTATION=0
SCALE=0.2
W=160
H=80
N=60
WW=20    

def read_image(filename):
    img = Image.open(filename)
    img.load()
    ## TODO Scaling
    img = img.resize( (int(img.size[0] * SCALE), int(img.size[1] * SCALE) ))
    if ROTATION:
        img = img.transpose(ROTATION)

    ## Center crop
    w, h = img.size
    if w < W or h < H:
        raise "Image too small for output"
    x1=(w - W) // 2
    y1=(h - H) // 2
    x2=x1+W
    y2=y1+H
    #print( "CROP %d, %d   %d %d %d %d" % (w, h, x1, y1, x2, y2))
    img = img.crop((x1, y1, x2, y2))
    return img

file_count = 0
lbl_count = 0


def wipe(image, wipe_column):
    img = image.convert('RGBA')
    pixels = img.load()
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            rgba = pixels[x, y]
            a = min(255, max(0, int( (wipe_column - x) * 255 / WW )))
            rgba = (rgba[0], rgba[1], rgba[2], a)
            pixels[x, y] = rgba
    return img

class LABEL:
    def __init__(self, lbl = None):
        if lbl:
            self.lbl = lbl
        else:
            global lbl_count
            self.lbl = "LBL%05d" % lbl_count
            lbl_count += 1

    def __str__(self):
        return "label %s" % self.lbl

class GOTO:
    def __init__(self, lbl):
        if isinstance(lbl, LABEL):
            lbl = lbl.lbl
        self.lbl = lbl

    def __str__(self):
        return "goto %s" % self.lbl
    
class IF(GOTO):
    def __init__(self, cond, lbl):
        if isinstance(lbl, LABEL):
            lbl = lbl.lbl
        self.cond = cond
        self.lbl = lbl

    def __str__(self):
        return "if %s goto %s" % (self.cond, self.lbl)

class IMG:
    def __init__(self, IMAGE):
        self.IMAGE = IMAGE
        self.filename = None

    def get_file_name(self):
        if not self.filename:
            global file_count
            self.filename = "tmp%05d.png" % file_count
            print("Generating %s" % self.filename)
            file_count+=1
            self.IMAGE.save(self.filename)
        return self.filename

    def __str__(self):
        return "file %s" % (self.get_file_name())

class FPS:
    def __init__(self, NUM, DENOM):
        self.NUM = NUM
        self.DENOM = DENOM

    def __str__(self):
        return "fps %d:%d" % (self.NUM, self.DENOM)

def make_wipe(FN):
    ret = [ FPS(1,3) ]
    image = read_image(FN);
    ret += [ IMG(image) ]
    ret += [ FPS(24, 1) ]
    for i in range(W, -WW, -3):
        ret += [ IMG(wipe(image, i)) ]
    return ret

    
def generate(commands, target):
    with open("tmp.pqoiml", "w") as f:
        for line in commands:
            f.write("%s\n" % line);
    os.system("cpqoi tmp.pqoiml >%s" % target);

generate(make_wipe("proffieos_logo_1.jpg"), "logo_wipe_160x80.pqf")

