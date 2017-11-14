#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk

from PIL import ImageTk, Image
from pprint import pprint
from fractions import Fraction

import argparse, re, os, sys
from datetime import date, time, datetime, timedelta
from collections import namedtuple
import csv

assert sys.version_info[0] > 2, "python 3 !"

p = argparse.ArgumentParser()
p.add_argument('--dir', default='.')
p.add_argument('-o', '--out', default='annotate.csv')
p.add_argument('--append', action='store_true', help='Append entries to csv')
p.add_argument('--header', action='store_true', help='Insert header with date')
p.add_argument('--ignore-empty', action='store_true', help='Do not output empty values')

p.add_argument('--boolean', action='store_true', help='Ask True (with keyboard J) or False (with keyboard F)')
p.add_argument('--true', action='store_true', help='What to write when True (J) (Right)', default='True')
p.add_argument('--false', action='store_true', help='What to write when False (F) (Left)', default='False')

p.add_argument('--width', type=int, default=800)
p.add_argument('--height', type=int, default=800)
p.add_argument('--rotate', type=int, choices=[0,90,180,270,-90,-180,-270], default=0, help='rotate all images by x degrees')

g = p.add_mutually_exclusive_group()
g.add_argument('--from-file', help='Take list of files from first column in csv file (in dir)')
g.add_argument('--ignore-file', help='Take list of files that are NOT in first column in csv file (in dir)')

p.add_argument('--continue', action='store_true', help='Continue previous work (ignore files in annotate.csv and append to it)')

a = args = p.parse_args()

if getattr(a, 'continue'):
    a.ignore_file = a.out
    a.append = True

def key_natural_sort(filename):
    """
    'File 28 Page 2' → ['File ', 28, ' Page ', 2]
    sorted(['1.png', '2.png', '3.png', '10.png', '20.png'], key=key_natural_sort) == ['1.png', '2.png', '3.png', '10.png', '20.png']
    """
    return [
        x if x else int(y)
        for x,y in re.compile('([^\\d]+)|(\\d+)').findall(filename)
    ]

def read_file_names(filename):
    ''' return first column of file <filename> '''
    with open(filename) as f:
        reader = csv.reader(f, delimiter=';')
        L = []
        for data in reader:
            if data:
                L.append(data[0])
        return L

if args.from_file:
    file_names = read_file_names(args.from_file)
else:
    file_names = os.listdir(args.dir)
    
    if args.ignore_file:
        if not os.path.exists(args.ignore_file):
            print('Warning, file ', args.ignore_file, 'does not exist to read ignore list')
        else:
            ignore_list = read_file_names(args.ignore_file)
            for l in ignore_list:
                try:
                    file_names.remove(l)
                except:
                    print('Warning, file ', l, 'does not exist to ignore')

FileInfo = namedtuple('FileInfo', ('path', 'name'))

files = sorted(
    [FileInfo(f,f) if args.dir == '.' else
     FileInfo(os.path.join(args.dir, f), f)
     for f in file_names
     if f.lower().endswith('.png')
     or f.lower().endswith('.jpg')],
    key=lambda fi: key_natural_sort(fi.name)
)

if args.append:
    opened_csv = open(args.out, 'a')
else:
    if os.path.exists(args.out):
        os.rename(args.out, args.out + datetime.now().strftime('.%Y-%m-%dT%Hh%S~'))
    opened_csv = open(args.out, 'w')
opened_csv_writer = csv.writer(opened_csv, delimiter=';')

if args.header:
    opened_csv_writer.writerow([
        datetime.now().strftime('-- %Y-%m-%dT%Hh%S --')
    ])
    opened_csv.flush()
    
root = Tk()
root.title("Annotate")

WIDTH, HEIGHT = args.width, args.height

def to_p1p2(R:'x,y,w,h'):
    x,y,w,h = R
    return x, y, x+w, y+h

def refresh_image():
    global image, photo
    image = (image_base
        .rotate(args.rotate)
        .resize(tuple(map(int, (image_base.width * zoom_factor, image_base.height * zoom_factor) )))
        .crop( to_p1p2((int(pos_image[0] * zoom_factor), int(pos_image[1] * zoom_factor), WIDTH,HEIGHT)) )
    )
    photo = ImageTk.PhotoImage(image)
    label.config(image=photo)

def onMouseDown(event):
    #print('D', event.x, event.y)
    global drag_point
    drag_point = event.x, event.y

def onMouseDownMove(event):
    #print('M', event.x, event.y)
    global image, photo, pos_image, drag_point
    
    dx = int((event.x - drag_point[0]) / zoom_factor)
    dy = int((event.y - drag_point[1]) / zoom_factor)
    pos_image = pos_image[0] - dx, pos_image[1] - dy
    
    drag_point = event.x, event.y
    
    refresh_image()

def onMouseUp(event):
    #print('U', event.x, event.y)
    global drag_point
    drag_point = None

def onScroll(event):
    global zoom_factor, photo, image
    if event.num == 4 or event.delta > 0:
        zoom_factor *= Fraction('1.1')
    if event.num == 5 or event.delta < 0:
        zoom_factor /= Fraction('1.1')
    #print('Zoom', float(zoom_factor))
    
    refresh_image()
    
def displayprop(x, L):
    pprint([getattr(x, l) for l in L])

def changeImage(direction, boolean=None):
    global file_index, image_base
    
    if args.boolean:
        output_variable = args.true if boolean else args.false
        output_line = True
    else:
        output_variable = text_variable.get().strip()
        if args.ignore_empty:
            output_line = output_variable != ''
        else:
            output_line = True 
    
    if output_line:
        opened_csv_writer.writerow([
            files[file_index].name,
            output_variable,
        ])
        opened_csv.flush()
    
    if file_index + direction >= len(files):
        opened_csv.close()
        root.quit()
    else:
        file_index = max(0, file_index + direction)
        image_base = Image.open(files[file_index].path)
        refresh_image()
    
    if not args.boolean:
        text_variable.set('')
    
    # print(file_index)

def onKeyDown(event):
    # event.keycode # event.keysym # event.keysym_num
    is_ctrl = event.keysym.startswith('Control')
    is_enter = event.keysym in ('Return', 'KP_Enter')
    # state == 16 → no modifiers
    # state == 20 → Ctrl is on
    
    if not args.boolean:
        if is_enter:
            changeImage(+1)
    else:
        if event.keysym == 'j':
            changeImage(+1, boolean=True)
        if event.keysym == 'f':
            changeImage(+1, boolean=False)
    # if event.state == 20 and event.keysym == 'Left':
    #     changeImage(-1)

file_index = 0
image_base = Image.open(files[file_index].path)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.pack() # fill=X, expand=True) # expand=True) # sticky=(N, W, E, S), expand=True)
# mainframe.columnconfigure(0, weight=1)
# mainframe.rowconfigure(0, weight=1)

if not args.boolean:
    text_variable = StringVar()

    text_variable_entry = ttk.Entry(mainframe, justify=CENTER, textvariable=text_variable)
    text_variable_entry.pack(side=BOTTOM, fill=X) # (column=0, row=1, sticky=(W, E))
else:
    ttk.Label(text='(F) False <-> True (J)').pack(side=BOTTOM, fill=X) # (column=0, row=1, sticky=(W, E))

pos_image = 0,0
zoom_factor = Fraction(1)
drag_point = None

label = ttk.Label(mainframe) # image=photo
label.pack(fill=BOTH, expand=True) # column=0, row=0)

refresh_image()

label.bind('<MouseWheel>', onScroll)
label.bind('<Button-4>', onScroll)
label.bind('<Button-5>', onScroll)
label.bind('<Button-1>', onMouseDown)
label.bind('<B1-Motion>', onMouseDownMove)
label.bind('<ButtonRelease-1>', onMouseUp)
# On Windows, you bind to <MouseWheel> and you need to divide event.delta by 120 (or some other factor depending on how fast you want the scroll)
# on OSX, you bind to <MouseWheel> and you need to use event.delta without modification
# on X11 systems you need to bind to <Button-4> and <Button-5>, and you need to divide event.delta by 120 → False, delta = 0, see event.num == 4|5 (or some other factor depending on how fast you want to scroll)

if not args.boolean:
    text_variable_entry.bind('<Key>', onKeyDown)
else:
    root.bind('<Key>', onKeyDown)
    
for child in mainframe.winfo_children():
    pass # child.grid_configure(padx=5, pady=5)

if not args.boolean:
    text_variable_entry.focus()
# root.bind('<Return>', calculate)

# def onResize(event):
    # global WIDTH, HEIGHT
    # WIDTH = event.width
    # HEIGHT = max(0, event.height - 50)
    # refresh_image()

# root.bind('<Configure>', onResize)

root.mainloop()
