#!/usr/bin/env python3
from tkinter import *
from tkinter import ttk

from PIL import ImageTk, Image
from pprint import pprint
from fractions import Fraction

import argparse
import re
import os
import sys
from datetime import date, time, datetime, timedelta
from collections import namedtuple
import csv

assert sys.version_info[0] > 2, "python 3 !"

# from tkinter.filedialog import askopenfilename
# askopenfilename()

from tkinter.simpledialog import messagebox as tkbox

p = argparse.ArgumentParser()
p.add_argument('files', nargs='*', help='files to annotate')
p.add_argument('--dir', default='.', help='files to read if neither files nor --from-files is given')
p.add_argument('-o', '--out', default='annotate.csv')
p.add_argument('--append', action='store_true', default=None, help='Append entries to csv')
p.add_argument('--header', action='store_true', help='Insert header with date')
p.add_argument('--ignore-empty', action='store_true', help='Do not output empty values')
# p.add_argument('--check', action='store_true', help='Do not write anything, just check current annotations')

p.add_argument('--boolean', action='store_true', help='Ask True (with keyboard J) or False (with keyboard F)')
p.add_argument('--true', default='True', help='When --boolean, what to write when True (J) (Right)')
p.add_argument('--false', default='False', help='When --boolean, what to write when False (F) (Left)')
p.add_argument('--allow-empty', action='store_true', help='When --boolean, allow pressing ENTER to let empty (may be combined with --ignore-empty)')
p.add_argument('--empty-value', default='', help='When --boolean and --allow-empty, what to write instead of the empty string when pressing ENTER')

p.add_argument('--width', type=int, default=800)
p.add_argument('--height', type=int, default=800)
p.add_argument('--rotate', type=int, choices=[0,90,180,270,-90,-180,-270], default=0, help='rotate all images by x degrees')
p.add_argument('--pos-x', type=int, default=0)
p.add_argument('--pos-y', type=int, default=0)
p.add_argument('--zoom', type=Fraction, default=1)

p.add_argument('--from-file', help='Take list of files from first column in from-file csv file (in dir)')
p.add_argument('--ignore-file', help='Take list of files that are NOT in first column in ignore-file csv file (in dir)')

p.add_argument('--continue', action='store_true', help='Continue previous work (ignore files in annotate.csv and append to it)')
p.add_argument('--new-column', action='store_true', help='Add new column in annotate.csv instead of creating new file. Order will be the one of annotate.csv, then normal order for the ones not present')

p.add_argument('--excel-dialect', help='Choose dialect of Excel based on language.', default='fr')
p.add_argument('--win-no-cd', action='store_true', help='On windows, the current working directory is guessed from argv[0] (right click behaviour). Write this for not doing that.')

a = args = p.parse_args()

if os.name == 'nt' and not args.win_no_cd:
    os.chdir(os.path.dirname(sys.argv[0]) or '.') # we right clicked on the file, so cd into the directory of the file

if getattr(a, 'continue'):
    assert a.append in (None, True), '--continue implies --append'
    a.append = True

if args.from_file:
    assert args.from_file.endswith('.csv'), "must be csv"
if args.ignore_file:
    assert args.ignore_file.endswith('.csv'), "must be csv"

if args.new_column:
    raise ValueError('not implemented')

# csv handling
class excel_french(csv.excel):
    delimiter = ';'

csv.register_dialect('excel_loc', excel_french if args.excel_dialect == 'fr' else
                                  csv.excel)

try:
    from natsort import natsort_keygen
    key_natural_sort = natsort_keygen()
except ImportError:
  def key_natural_sort(filename):
    """
    >>> key_natural_sort('File 28 Page 2')
    ['File ', '0000000028', ' Page ', '0000000002']
    
    >>> sorted(['1.png', '2.png', '3.png', '10.png', '20.png'], key=key_natural_sort)
    ['1.png', '2.png', '3.png', '10.png', '20.png']
    
    """
    return [
        x if x else y.zfill(10) # int(y)
        for x,y in re.compile('([^\\d]+)|(\\d+)').findall(filename)
    ]

def read_file_names(filename):
    ''' return first column of file <filename> '''
    with open(filename, newline='') as f:
        return [data[0] for data in csv.reader(f, dialect='excel_loc') if data]

file_names = []

if args.files:
    file_names += args.files

if args.from_file:
    file_names += read_file_names(args.from_file)

if file_names == []:
    my_sort = lambda S: sorted(S, key=key_natural_sort)
    
    file_names += my_sort(
        f if args.dir == '.' else
        os.path.join(args.dir, f)
        for f in os.listdir(args.dir))
    
if args.ignore_file:
    if not os.path.exists(args.ignore_file):
        print('Warning, file ', args.ignore_file, 'does not exist to read ignore list')
    else:
        ignore_list = read_file_names(args.ignore_file)
        print('- INFO Ignored {}: {}'.format(len(ignore_list), ', '.join(ignore_list[:5]) + '...' * (len(ignore_list) > 5)))
        for l in ignore_list:
            try:
                file_names.remove(l)
            except:
                print('Warning, file ', l, 'does not exist to ignore')

if os.path.exists(args.out) and (args.new_column or getattr(args, 'continue')):
    ignore_list = read_file_names(args.out)
    for l in ignore_list:
        try:
            file_names.remove(l)
        except:
            print('Warning, file ', l, 'does not exist to ignore')
    if args.new_column:
        ... # TODO: new_column

files = [f for f in file_names
         if f.lower().endswith('.png')
         or f.lower().endswith('.jpg')]

if args.append:
    opened_csv = open(args.out, 'a', newline='')
else:
    if os.path.exists(args.out):
        try:
            os.rename(args.out, args.out + datetime.now().strftime('.%Y-%m-%dT%Hh%S~'))
        except Exception as e:
            tkbox.showwarning('Error', str(e))
            raise e
    opened_csv = open(args.out, 'w', newline='')
opened_csv_writer = csv.writer(opened_csv, dialect='excel_loc')

if args.header:
    opened_csv_writer.writerow([
        datetime.now().strftime('-- %Y-%m-%dT%Hh%S --')
    ])
    opened_csv.flush()
    
root = Tk()
root.title("Annotate")

root.geometry("{}x{}+{}+{}".format(args.width, args.height, 0, 0))

def to_p1p2(R:'x,y,w,h'):
    x,y,w,h = R
    return x, y, x+w, y+h

def refresh_image():
    global image, photo
    image = (image_base
        .rotate(rotate_angle)
        .resize(tuple(map(int, (image_base.width * zoom_factor, image_base.height * zoom_factor) )))
    )
    # image = image.crop( to_p1p2((int(pos_image[0] * zoom_factor), int(pos_image[1] * zoom_factor), image.width,image.height)) )
    # image = image.crop( to_p1p2((0, 0, image.width,image.height)) )
    
    photo = ImageTk.PhotoImage(image)
    label.delete(ALL)
    label.create_image((int(- pos_image[0] * zoom_factor) + image.width//2, int(- pos_image[1] * zoom_factor) + image.height//2),image=photo)
    # label.config(image=photo)

def onMouseDown(event):
    global drag_point
    drag_point = event.x, event.y

def onMouseDownMove(event):
    global image, photo, pos_image, drag_point
    
    dx = int((event.x - drag_point[0]) / zoom_factor)
    dy = int((event.y - drag_point[1]) / zoom_factor)
    pos_image = pos_image[0] - dx, pos_image[1] - dy
    
    drag_point = event.x, event.y
    
    refresh_image()

def onMouseUp(event):
    print('--pos-x={} --pos-y={}'.format(*pos_image))
    global drag_point
    drag_point = None

def onScroll(event):
    if event.num == 4 or event.delta > 0:
        onZoom(1)
    if event.num == 5 or event.delta < 0:
        onZoom(-1)
    
def displayprop(x, L):
    pprint([getattr(x, l) for l in L])

def changeImage(direction, boolean=None):
    global file_index, image_base
    
    if args.boolean:
        output_variable = args.true if boolean == True else args.false if boolean == False else args.empty_value
    else:
        output_variable = text_variable.get().strip()
        
    if args.ignore_empty:
        output_line = output_variable != ''
    else:
        output_line = True 
    
    if output_line:
        opened_csv_writer.writerow([
            files[file_index],
            output_variable,
        ])
        opened_csv.flush()
    
    if file_index + direction >= len(files):
        opened_csv.close()
        root.quit()
    else:
        file_index = max(0, file_index + direction)
        image_base = Image.open(files[file_index])
        infovariable.set("{} ({}/{})".format(files[file_index], 1+file_index, len(files)))
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
        if args.allow_empty and is_enter:
            changeImage(+1, boolean=None)
    # if event.state == 20 and event.keysym == 'Left':
    #     changeImage(-1)

def onRotate(direction):
    global rotate_angle
    
    rotate_angle += direction * 90
    if abs(rotate_angle) >= 360:
        rotate_angle %= 360
    
    print('--rotate={}'.format(rotate_angle))
    
    refresh_image()

def onZoom(direction):
    global zoom_factor
    
    zoom_factor *= Fraction('1.1') ** direction # (f *= 1.1) if d = +1 else (f /= 1.1) if d = -1 else (f *= 1.1 * 1.1) if d = +2 etc.
    
    print('--zoom={}'.format(zoom_factor))
    
    refresh_image()

# BEGIN GUI

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.pack(fill=BOTH, expand=True) # fill=X, expand=True) # expand=True) # sticky=(N, W, E, S), expand=True)
# mainframe.columnconfigure(0, weight=1)
# mainframe.rowconfigure(0, weight=1)

infovariable = StringVar()
infovariable_label = ttk.Label(mainframe, textvariable=infovariable, anchor=S)
infovariable_label.pack(fill=X, side=TOP)
infovariable_label.bind('<Button-1>', lambda x: print(infovariable.get()))

# ttk.Button(mainframe, text='Zoom -', command=lambda: onZoom(1)).pack(side=BOTTOM)
ttk.Button(mainframe, text='Rotate', command=lambda: onRotate(+1)).pack(side=BOTTOM)
# ttk.Button(mainframe, text='Zoom +', command=lambda: onZoom(-1)).pack(side=BOTTOM)

if args.boolean:
    widget = ttk.Entry(mainframe, justify=CENTER)
    widget.insert(0, '(F) False <-> True (J)')
    widget.config(state=DISABLED)
else:
    text_variable = StringVar()

    widget = text_variable_entry = ttk.Entry(mainframe, justify=CENTER, textvariable=text_variable)

widget.pack(side=BOTTOM, anchor=S) # (column=0, row=1, sticky=(W, E))

# END GUI

file_index = 0
image_base = Image.open(files[file_index])
infovariable.set("{} ({}/{})".format(files[file_index], 1+file_index, len(files)))

pos_image = args.pos_x, args.pos_y
zoom_factor = args.zoom
rotate_angle = args.rotate
drag_point = None

label = Canvas(mainframe) # image=photo
label.pack(fill=BOTH, expand=True) # column=0, row=0)

refresh_image()

label.bind('<MouseWheel>', onScroll)
label.bind('<Button-4>', onScroll)
label.bind('<Button-5>', onScroll)
label.bind('<Button-1>', onMouseDown)
label.bind('<Double-Button-1>', lambda x:onRotate(+1))
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
    
def onResize(event):
    print('--width={} --height={}'.format(event.width, event.height))
    # event.x event.y event.x_root event.y_root
    
root.bind("<Configure>", onResize)

root.mainloop()

# import os
# print(sys.version_info)
# os.system("pause")
