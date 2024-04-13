import customtkinter
from tknodesystem import *
from openai import OpenAI
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

# 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
api_key = input('Please input the openai key: ')
client = OpenAI(api_key=api_key)

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
    dialog = MultiLineInputDialog(root, title="Input", prompt="Type in the LinkedIn article prompt: ")
    text = dialog.input_text
    if text is not None:
        NodeValue(canvas, text=f"Value {text}", value=text)

def getConcept(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a data developer at a company called CMI2I. You are contributing to articles in Data Engineering, so make sure to talk about everything from a data engineering perspective."},
            {"role": "user",
             "content": f"Come up with 1 real-world concept name related to {prompt}, write it in a single line. This concept MUST be a name of a term related to data science and must be widely used in the industry"}
        ]
    )
    concept_name = completion.choices[0].message.content
    print(f"Relevant concept: {concept_name}")
    return concept_name

def writeArticle(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a data developer at a company called CMI2I. You are contributing to articles in Data Engineering, so make sure to talk about everything from a data engineering perspective."},
            {"role": "user",
             "content": f"Write a 1 short paragraph contribution to a LinkedIn collaborative article basing it off the prompt: {prompt}"}
        ]
    )
    article = completion.choices[0].message.content
    print(f"Relevant concept: {article}")
    return article


menu = NodeMenu(canvas)  # right click or press <space> to spawn the node menu
menu.add_node(label="Value", command=add_value)
menu.add_node(label="Print Concept", command=lambda: NodeOperation(canvas, inputs=1, text="Concept", command=getConcept))
menu.add_node(label="Write Contribution", command=lambda: NodeOperation(canvas, inputs=1, text="Article", command=writeArticle))
# Perform Anti-AI
# menu.add_node(label="Write Contribution", command=lambda: NodeOperation(canvas, inputs=1, text="Concept", command=getConcept))
menu.add_node(label="Output", command=lambda: NodeCompile(canvas))

root.mainloop()