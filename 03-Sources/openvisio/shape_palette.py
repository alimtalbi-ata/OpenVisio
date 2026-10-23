"""Docked Tk equipment catalogue, designed for OpenVisio's Editor.
Author: Abdelhalim Talbi.
"""
import tkinter as tk
from .shapes import SHAPES

def install_palette(editor):
    panel = tk.Frame(editor, width=188, bg="#e8eef6")
    panel.pack(side="left", fill="y", before=editor.canvas)
    panel.pack_propagate(False)
    tk.Label(panel, text="BIBLIOTHÈQUE", bg="#e8eef6",
             font=("Arial", 11, "bold")).pack(pady=(12, 6))
    listing = tk.Listbox(panel, exportselection=False, activestyle="dotbox")
    kinds = list(SHAPES)
    for kind in kinds:
        listing.insert("end", SHAPES[kind]["label"])
    listing.pack(fill="both", expand=True, padx=8, pady=4)
    listing.selection_set(0)
    def place(event=None):
        selected = listing.curselection()
        kind = kinds[selected[0]] if selected else "server"
        x, y = editor.viewport.world(editor.canvas.winfo_width()/2,
                                     editor.canvas.winfo_height()/2)
        editor.create_node(x, y, kind=kind)
    tk.Button(panel, text="Placer au centre", command=place).pack(
        fill="x", padx=8, pady=(4, 12))
    listing.bind("<Double-Button-1>", place)
    return panel
