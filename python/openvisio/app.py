"""Native Tkinter diagram editor. Author: Abdelhalim Talbi."""
import tkinter as tk
from tkinter import filedialog, messagebox
from uuid import uuid4
from .model import load, save

class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenVisio 42.0 — Python natif")
        self.geometry("1100x720")
        self.document = {"nodes": [], "edges": []}
        self.current_path = None
        self.selected = None
        self.link_start = None
        self.canvas = tk.Canvas(self, bg="#f8fafc", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Double-Button-1>", self.add_node)
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<Configure>", lambda event: self.draw())
        bar = tk.Menu(self)
        filemenu = tk.Menu(bar, tearoff=False)
        for label, command in [("Nouveau", self.new), ("Ouvrir", self.open), ("Enregistrer", self.store), ("Enregistrer sous", self.store_as)]:
            filemenu.add_command(label=label, command=command)
        bar.add_cascade(label="Fichier", menu=filemenu)
        edit = tk.Menu(bar, tearoff=False)
        edit.add_command(label="Ajouter un équipement", command=lambda: self.create_node(150, 120))
        edit.add_command(label="Relier deux équipements", command=self.begin_link)
        edit.add_command(label="Supprimer la sélection", command=self.delete_selected)
        bar.add_cascade(label="Édition", menu=edit)
        self.config(menu=bar)
        self.bind("<Control-s>", lambda event: self.store())
        self.bind("<Control-o>", lambda event: self.open())
        self.bind("<Delete>", lambda event: self.delete_selected())
        self.status = tk.StringVar(value="Double-clic : ajouter | Glisser : déplacer | Édition : relier")
        tk.Label(self, textvariable=self.status, anchor="w").pack(fill="x")
    def new(self):
        self.document = {"nodes": [], "edges": []}
        self.current_path = None
        self.selected = None
        self.draw()
    def create_node(self, x, y):
        node = {"id": uuid4().hex, "x": round(x), "y": round(y), "label": "Équipement"}
        self.document["nodes"].append(node)
        self.selected = node["id"]
        self.draw()
    def add_node(self, event):
        self.create_node(event.x, event.y)
    def node_at(self, x, y):
        for node in reversed(self.document["nodes"]):
            if abs(node["x"]-x) <= 70 and abs(node["y"]-y) <= 30:
                return node
        return None
    def click(self, event):
        node = self.node_at(event.x, event.y)
        if self.link_start is not None and node is not None:
            if node["id"] != self.link_start:
                self.document["edges"].append({"id": uuid4().hex, "from": self.link_start, "to": node["id"]})
            self.link_start = None
        self.selected = node["id"] if node else None
        self.draw()
    def drag(self, event):
        node = next((n for n in self.document["nodes"] if n["id"] == self.selected), None)
        if node:
            node["x"], node["y"] = event.x, event.y
            self.draw()
    def begin_link(self):
        if not self.selected:
            messagebox.showinfo("Connexion", "Sélectionnez d'abord un équipement")
            return
        self.link_start = self.selected
        self.status.set("Cliquez sur le second équipement pour créer la connexion")
    def delete_selected(self):
        sid = self.selected
        self.document["nodes"] = [n for n in self.document["nodes"] if n["id"] != sid]
        self.document["edges"] = [e for e in self.document["edges"] if e["from"] != sid and e["to"] != sid]
        self.selected = None
        self.draw()
    def draw(self):
        self.canvas.delete("all")
        by_id = {n["id"]: n for n in self.document["nodes"]}
        for edge in self.document["edges"]:
            a, b = by_id.get(edge["from"]), by_id.get(edge["to"])
            if a and b:
                self.canvas.create_line(a["x"], a["y"], b["x"], b["y"], fill="#2563eb", width=2, arrow=tk.LAST)
        for n in self.document["nodes"]:
            x, y = n["x"], n["y"]
            selected = n["id"] == self.selected
            self.canvas.create_rectangle(x-70, y-30, x+70, y+30, fill="#dbeafe" if selected else "white", outline="#1d4ed8", width=3 if selected else 1)
            self.canvas.create_text(x, y, text=n.get("label", "Équipement")[:40], fill="#172554")
    def open(self):
        path = filedialog.askopenfilename(filetypes=[("OpenVisio JSON", "*.ovjson *.json")])
        if not path: return
        try:
            self.document = load(path)
            self.current_path = path
            self.selected = None
            self.draw()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Ouverture impossible", str(exc))
    def store(self):
        if not self.current_path: return self.store_as()
        try:
            save(self.current_path, self.document)
            self.status.set("Enregistré : " + self.current_path)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Enregistrement impossible", str(exc))
    def store_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".ovjson", filetypes=[("OpenVisio", "*.ovjson")])
        if path:
            self.current_path = path
            self.store()

def main():
    Editor().mainloop()
