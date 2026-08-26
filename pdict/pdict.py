#!/usr/bin/env python3.14

import json
try:
    first_pdict = json.load(open('pdict.json'))
except:
    first_pdict = {}
try:
    additional = json.load(open('additional.json'))
except:
    additional = {}

pdict = first_pdict | additional

import tkinter as tk
from tkinter import ttk
root = tk.Tk()
root.geometry("300x200")
root.title("Pdict app")

l = ttk.Label(text="Lookup:")
l.pack(fill="x")
entry = ttk.Entry(root)
entry.pack(fill="x")
out = ttk.Entry(root)
out.pack(fill="x")
ok = ttk.Button(text="Ok")
ok.pack(fill="x")

labelcc = ttk.Label(root, text="Copied to clipboard!")
labelcc.pack()
labelcc.pack_forget()
l = labelerror = ttk.Label(root, text="Not found in pdict!")
l.pack(fill="x")
l.pack_forget()

#l = ttk.Label(text="Add new word:")
#l.pack(fill="x")

#label_key = l = ttk.Label(root, text="Key:")
#l.pack(fill="x")

#key = ttk.Entry()
#key.pack(fill="x")

#l = ttk.Label(root, text="Value:")
#l.pack(fill="x")

#value = ttk.Entry()
#value.pack(fill="x")

def save_new_word():
    if not (entry.get() and out.get()):
        return
    global pdict, additional
    additional[entry.get()] = out.get()
    pdict = first_pdict | additional
    json.dump(additional, open('additional.json', 'w'), indent=4)
    label_saved['text'] = "Saved !"
    root.after(2000, lambda: label_saved.config(text=''))

button = ttk.Button(root, text="Save new word", command=save_new_word)
button.pack()

label_saved = l = ttk.Label(root, text="")
l.pack()

entry.focus()

def run(ev: tk.Event):
    #out.delete(0, tk.END)
    #out.insert(0, mapping := pdict.get(entry.get(), entry.get()))
    
    root.clipboard_clear()
    root.clipboard_append(out.get())
    labelcc.pack()
    labelerror.pack_forget()
    ev.widget.delete(0, tk.END)
    root.update() # mandatory for clipboard to keep after destroy
    root.after(10, root.destroy)
    # root.after(300, root.destroy)

    #if pdict.get(entry.get()):
    #else:
        #labelcc.pack_forget()
        #labelerror.pack()

def on_key(ev: tk.Event):
    mapping = pdict.get(entry.get(), entry.get())
    out.delete(0, tk.END)
    out.insert(0, mapping)
    ok['text'] = f'Copy: "{mapping}"'
    #label_key['text'] = f"Key: {entry.get()}"

entry.bind('<Control-BackSpace>', lambda ev: ev.widget.delete(0, tk.END))
entry.bind('<KeyRelease>', on_key)
entry.bind('<Return>', run)
out.bind('<Control-BackSpace>', lambda ev: ev.widget.delete(0, tk.END))
ok.bind('<Button-1>', run)
root.bind('<Escape>', lambda ev: root.destroy())
#value.bind('<Return>', lambda ev: save_new_word())

root.mainloop()
