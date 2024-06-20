#!/usr/bin/env python3

import numpy as np
from PIL import Image
import os
import random

ROTATION=Image.ROTATE_90
SCALE=0.5
W=160
H=80
N=60
FILE_PATTERN="images/COLOR/STYLE/crystal_chamber_COLOR_STYLE_%04d.jpg"

    

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

def mix_color(filename, RGB):
    red = read_image(filename.replace("COLOR", "red"))
    green = read_image(filename.replace("COLOR", "green"))
    blue = read_image(filename.replace("COLOR", "blue"))
    return np.asarray(red) * RGB[0] + np.asarray(green) * RGB[1] + np.asarray(blue) * RGB[2]

def mix_brightness(filename, RGB, NBSB):
    normal = mix_color(filename.replace("STYLE", "normal"), RGB)
    bright_simple = mix_color(filename.replace("STYLE", "bright_simple").replace("_bright_simple_", "_bright_"), RGB)
    bright = mix_color(filename.replace("STYLE", "bright"), RGB)
    return normal * NBSB[0] + bright_simple * NBSB[1] + bright * NBSB[2]


file_count = 0
lbl_count = 0

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
    def __init__(self, N, RGB, NBSB):
        self.N = N
        self.RGB = RGB
        self.NBSB = NBSB
        self.filename = None

    def get_file_name(self):
        if not self.filename:
            global file_count
            self.filename = "tmp%05d.png" % file_count
            print("Generating %s" % self.filename)
            file_count+=1
            i = Image.fromarray(
                mix_brightness(FILE_PATTERN % self.N, self.RGB, self.NBSB).astype(np.uint8)
            )
            i.save(self.filename)
        return self.filename

    def __str__(self):
        return "file %s" % (self.get_file_name())

class FPS:
    def __init__(self, NUM, DENOM):
        self.NUM = NUM
        self.DENOM = DENOM

    def __str__(self):
        return "fps %d:%d" % (self.NUM, self.DENOM)


def make_simple_loop(N, RGB, NBSB):
    ret = [ FPS(30, 1) ]
    start = LABEL()
    ret.append(start)
    for i in range(0, N):
        ret.append(IMG(i, RGB, NBSB))
    ret.append(GOTO(start))
    return ret

def make(RGB):
    global N
    ret = [ FPS(30, 1) ]
    
    ret.append(LABEL("off_start"))
    for i in range(0, N):
        ret.append(IF("ison", "on_loop%d" % i))
        ret.append(LABEL("off_loop%d" % i))
        ret.append(IMG(i, RGB, [1.0, 0.0, 0.0]))
    ret.append(GOTO("off_start"))

    ret.append(LABEL("on_start"))
    
    for i in range(0, N):
        if i % 3:
            ret.append(LABEL("on_loop%d" % i))
            continue
        ret.append(IF("ison", "on_loop%d" % i))
        ret.append(GOTO("off_loop%d" % i))
        ret.append(LABEL("on_loop%d" % i))
        ret.append(IF("drag", "bright_loop%d" % i))
        ret.append(IF("lock", "bright_loop%d" % i))
        ret.append(IF("clsh", "bright_loop%d" % i))
        ret.append(IMG(i, RGB, [0.0, 1.0, 0.0]))
    ret.append(GOTO("on_start"))

    ret.append(LABEL("bright_start"))
    for i in range(0, N):
        if i % 3:
            ret.append(LABEL("bright_loop%d" % i))
            continue
        ret.append(IF("drag", "bright_loop%d" % i))
        ret.append(IF("lock", "bright_loop%d" % i))
        ret.append(IF("clsh", "bright_loop%d" % i))
        ret.append(GOTO("on_loop%d" % i))
        ret.append(LABEL("bright_loop%d" % i))
#        r = random.random() / 0.5
#        ret.append(IMG(i, RGB, [0.0, r, 1.0 - r]))
        ret.append(IMG(i, RGB, [0.0, 0.0, 1.0]))
    ret.append(GOTO("bright_start"))
                   
    return ret

    
def generate(commands, target):
    with open("tmp.pqoiml", "w") as f:
        for line in commands:
            f.write("%s\n" % line);
    os.system("cpqoi tmp.pqoiml >%s" % target);


#pqoi = make_simple_loop(60, [0.5, 0.0, 0.5], [1.0, 0.0, 0.0])

#pqoi = make([0.5, 0.0, 0.5])
#generate(pqoi, "vcrystal.pqf")

generate(make([1.0, 0.0, 0.0]), "vc_160x80_red.pqf")
generate(make([0.0, 1.0, 0.0]), "vc_160x80_green.pqf")
generate(make([0.0, 0.0, 1.0]), "vc_160x80_blue.pqf")
generate(make([0.5, 0.5, 0.0]), "vc_160x80_yellow.pqf")
generate(make([0.5, 0.0, 0.5]), "vc_160x80_purple.pqf")
generate(make([0.0, 0.5, 0.5]), "vc_160x80_cyan.pqf")
