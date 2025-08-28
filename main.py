#!/usr/bin/env python

import tkinter as tk

root = tk.Tk()
root.geometry("1280x960")

for i in range(0, 3):
    root.columnconfigure(i, weight=1)
    root.rowconfigure(i, weight=1)

button = tk.Button(root, text="Example")
button.grid(row=0, column=0, sticky="NSEW")

button2 = tk.Button(root, text="Example2")
button2.grid(row=1, column=0, sticky="NSEW")


button3 = tk.Button(root, text="Example3")
button3.grid(row=2, column=0, sticky="NSEW")



if __name__ == "__main__":
    root.mainloop()
