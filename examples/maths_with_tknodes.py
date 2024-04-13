# Example of TkNodeSystem
# Author: Akash Bora
# License: MIT

import customtkinter 
from tknodesystem import *
import tkinter as tk
from tkinter import simpledialog

root = customtkinter.CTk()
root.geometry("800x500")
root.title("AI Content Maker")

canvas = NodeCanvas(root)
canvas.pack(fill="both", expand=True)

canvas.rowconfigure(0, weight=1)
button_1 = customtkinter.CTkButton(canvas, text="save", width=50, command=lambda: canvas.save("canvas.json"))
button_1.grid(pady=10, padx=10, sticky="se")

button_2 = customtkinter.CTkButton(canvas, text="load", width=50, command=lambda: canvas.load("canvas.json"))
button_2.grid(pady=10, padx=10, sticky="se")

class MultiLineInputDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, prompt="", initial_value=""):
        self.prompt = prompt
        self.initial_value = initial_value
        self.input_text = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text=self.prompt).pack()
        self.text_widget = tk.Text(master, width=40, height=10)
        self.text_widget.pack()
        self.text_widget.insert('1.0', self.initial_value)
        return self.text_widget

    def apply(self):
        self.input_text = self.text_widget.get('1.0', 'end-1c')

def add_value():
    root = tk.Tk()  # This is just for demonstration; use your existing Tk instance
    dialog = MultiLineInputDialog(root, title="Value Node", prompt="Type in a number:")
    root.mainloop()
    text = dialog.input_text
    if text is not None and text.isdigit():
        NodeValue(canvas, text=f"Value {text}", value=int(text))

def add(x,y):
    return x+y

def power(x,y):
    return x**y

def sub(x,y):
    return x-y
    
def div(x,y):
    if y!=0:
        return x/y
    else:
        return None
    
def mul(x,y):
    return x*y

def mod(x):
    return abs(x)

menu = NodeMenu(canvas) # right click or press <space> to spawn the node menu
menu.add_node(label="Value", command=add_value)
menu.add_node(label="Output", command=lambda: NodeCompile(canvas))
menu.add_node(label="Add/Sum", command=lambda: NodeOperation(canvas, text="Add", command=add))
menu.add_node(label="Subtract", command=lambda: NodeOperation(canvas, text="Sub", command=sub))
menu.add_node(label="Divide", command=lambda: NodeOperation(canvas, text="Div", command=div))
menu.add_node(label="Mod", command=lambda: NodeOperation(canvas, inputs=1, text="Mod", command=mod))
menu.add_node(label="Multiply", command=lambda: NodeOperation(canvas, text="Mul", command=mul))
menu.add_node(label="Power", command=lambda: NodeOperation(canvas, text="Power", command=power))
root.mainloop()
