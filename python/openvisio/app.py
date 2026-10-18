"""Native Tkinter diagram editor. Author: Abdelhalim Talbi."""
import tkinter as tk
import json
from tkinter import filedialog, messagebox, simpledialog
from uuid import uuid4
from .model import load, save
from .export import export_svg
from .shapes import SHAPES, get_shape
from .properties import normalize_properties
from .links import normalize_link, PROTOCOLS
from .history import History
from .render import node_at, edge_at, draw_document

class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenVisio 42.0 — Python natif")
        self.geometry("1100x720")
        self.document = {"nodes": [], "edges": []}
        self.current_path = None
        self.selected = None
        self.selected_edge = None
        self.link_start = None
        self.history = History(self.document)
        self.saved_snapshot = self._snapshot()
        self.protocol("WM_DELETE_WINDOW", self.close_safely)
        self.canvas = tk.Canvas(self, bg="#f8fafc", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Double-Button-1>", self.add_node)
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", lambda event: self._record_change())
        self.canvas.bind("<Configure>", lambda event: self.draw())
        bar = tk.Menu(self)
        filemenu = tk.Menu(bar, tearoff=False)
        for label, command in [("Nouveau", self.new), ("Ouvrir", self.open), ("Enregistrer", self.store), ("Enregistrer sous", self.store_as), ("Exporter en SVG", self.export_as_svg)]:
            filemenu.add_command(label=label, command=command)
        bar.add_cascade(label="Fichier", menu=filemenu)
        edit = tk.Menu(bar, tearoff=False)
        edit.add_command(label="Annuler", command=self.undo)
        edit.add_command(label="Rétablir", command=self.redo)
        edit.add_separator()
        edit.add_command(label="Ajouter un équipement", command=lambda: self.create_node(150, 120))
        edit.add_command(label="Relier deux équipements", command=self.begin_link)
        edit.add_command(label="Propriétés de la sélection", command=self.edit_properties)
        edit.add_command(label="Propriétés de la liaison sélectionnée", command=self.edit_selected_link)
        edit.add_command(label="Supprimer la sélection", command=self.delete_selected)
        bar.add_cascade(label="Édition", menu=edit)
        shapes_menu = tk.Menu(bar, tearoff=False)
        for key, shape in SHAPES.items():
            shapes_menu.add_command(label=shape["label"], command=lambda kind=key: self.create_node(180, 140, kind))
        bar.add_cascade(label="Équipements", menu=shapes_menu)
        self.config(menu=bar)
        self.bind("<Control-z>", lambda event: self.undo())
        self.bind("<Control-y>", lambda event: self.redo())
        self.bind("<Control-s>", lambda event: self.store())
        self.bind("<Control-o>", lambda event: self.open())
        self.bind("<Delete>", lambda event: self.delete_selected())
        self.bind("<F2>", lambda event: self.edit_properties())
        self.status = tk.StringVar(value="Double-clic : ajouter | Glisser : déplacer | Édition : relier")
        tk.Label(self, textvariable=self.status, anchor="w").pack(fill="x")
    def _record_change(self):
        self.history.record(self.document)
    def undo(self):
        document = self.history.undo()
        if document is not None:
            self.document = document
            self.selected = self.selected_edge = None
            self.draw()
    def redo(self):
        document = self.history.redo()
        if document is not None:
            self.document = document
            self.selected = self.selected_edge = None
            self.draw()
    def _snapshot(self):
        return json.dumps(self.document, sort_keys=True, ensure_ascii=False)
    def _confirm_discard(self):
        if self._snapshot() == self.saved_snapshot:
            return True
        answer = messagebox.askyesnocancel("Modifications non enregistrées", "Enregistrer les modifications avant de continuer ?", parent=self)
        if answer is None:
            return False
        if answer:
            self.store()
            return self._snapshot() == self.saved_snapshot
        return True
    def close_safely(self):
        if self._confirm_discard():
            self.destroy()
    def new(self):
        if not self._confirm_discard():
            return
        self.document = {"nodes": [], "edges": []}
        self.current_path = None
        self.selected = None
        self.selected_edge = None
        self.saved_snapshot = self._snapshot()
        self.history.reset(self.document)
        self.draw()
    def create_node(self, x, y, kind="server"):
        node = {"id": uuid4().hex, "x": round(x), "y": round(y), "label": get_shape(kind)["label"], "shape": kind}
        self.document["nodes"].append(node)
        self._record_change()
        self.selected = node["id"]
        self.draw()
    def add_node(self, event):
        self.create_node(event.x, event.y)
    def node_at(self, x, y):
        return node_at(self.document["nodes"], x, y)
    def edge_at(self, x, y):
        return edge_at(self.document["nodes"], self.document["edges"], x, y)
    def click(self, event):
        node = self.node_at(event.x, event.y)
        if self.link_start is not None and node is not None:
            if node["id"] != self.link_start:
                self.document["edges"].append({"id": uuid4().hex, "from": self.link_start, "to": node["id"]})
                self._record_change()
            self.link_start = None
        self.selected = node["id"] if node else None
        self.selected_edge = None if node else (self.edge_at(event.x, event.y) or {}).get("id")
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
    def edit_properties(self):
        node = next((n for n in self.document["nodes"] if n["id"] == self.selected), None)
        if node is None:
            messagebox.showinfo("Propriétés", "Sélectionnez un équipement")
            return
        dialog = tk.Toplevel(self)
        dialog.title("Propriétés de l'équipement")
        dialog.transient(self)
        dialog.grab_set()
        fields = {}
        for row, (key, title) in enumerate((("label", "Nom"), ("hostname", "Hôte / FQDN"), ("address", "Adresse IP"), ("vendor", "Constructeur"), ("model", "Modèle"))):
            tk.Label(dialog, text=title, anchor="w").grid(row=row, column=0, padx=12, pady=6, sticky="w")
            value = tk.StringVar(value=node.get(key, ""))
            tk.Entry(dialog, textvariable=value, width=42).grid(row=row, column=1, padx=12, pady=6)
            fields[key] = value
        def apply():
            try:
                values = normalize_properties(**{key: value.get() for key, value in fields.items()})
            except ValueError as exc:
                messagebox.showerror("Propriétés invalides", str(exc), parent=dialog)
                return
            node.update(values)
            self._record_change()
            self.draw()
            dialog.destroy()
        tk.Button(dialog, text="Enregistrer", command=apply).grid(row=5, column=1, pady=12, sticky="e")
        dialog.bind("<Return>", lambda event: apply())
        dialog.bind("<Escape>", lambda event: dialog.destroy())
        dialog.wait_window()
    def edit_selected_link(self):
        if not self.document["edges"]:
            messagebox.showinfo("Liaisons", "Créez d'abord une connexion")
            return
        edge = next((e for e in self.document["edges"] if e["id"] == self.selected_edge), None)
        if edge is None:
            messagebox.showinfo("Liaisons", "Cliquez sur une liaison pour la sélectionner")
            return
        dialog = tk.Toplevel(self)
        dialog.title("Propriétés de la liaison SAN")
        dialog.transient(self)
        dialog.grab_set()
        fields = {}
        for row, (key, title) in enumerate((("protocol", "Protocole"), ("source_port", "Port source"), ("target_port", "Port cible"), ("fabric", "Fabric"), ("speed_gbps", "Débit (Gbit/s)"))):
            tk.Label(dialog, text=title).grid(row=row, column=0, padx=12, pady=6, sticky="w")
            value = tk.StringVar(value=edge.get(key, "FC" if key == "protocol" else ""))
            if key == "protocol":
                tk.OptionMenu(dialog, value, *PROTOCOLS).grid(row=row, column=1, padx=12, pady=6, sticky="ew")
            else:
                tk.Entry(dialog, textvariable=value, width=38).grid(row=row, column=1, padx=12, pady=6)
            fields[key] = value
        def apply():
            try:
                edge.update(normalize_link(**{key: value.get() for key, value in fields.items()}))
                self._record_change()
            except ValueError as exc:
                messagebox.showerror("Liaison invalide", str(exc), parent=dialog)
                return
            self.draw()
            dialog.destroy()
        tk.Button(dialog, text="Enregistrer", command=apply).grid(row=5, column=1, pady=12, sticky="e")
        dialog.bind("<Escape>", lambda event: dialog.destroy())
        dialog.wait_window()
    def delete_selected(self):
        sid = self.selected
        if self.selected_edge:
            self.document["edges"] = [e for e in self.document["edges"] if e["id"] != self.selected_edge]
            self.selected_edge = None
        self.document["nodes"] = [n for n in self.document["nodes"] if n["id"] != sid]
        self.document["edges"] = [e for e in self.document["edges"] if e["from"] != sid and e["to"] != sid]
        self.selected = None
        self._record_change()
        self.draw()
    def draw(self):
        draw_document(self.canvas, self.document, self.selected, self.selected_edge)
    def open(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(filetypes=[("OpenVisio JSON", "*.ovjson *.json")])
        if not path: return
        try:
            self.document = load(path)
            self.current_path = path
            self.selected = None
            self.selected_edge = None
            self.saved_snapshot = self._snapshot()
            self.history.reset(self.document)
            self.draw()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Ouverture impossible", str(exc))
    def store(self):
        if not self.current_path: return self.store_as()
        try:
            save(self.current_path, self.document)
            self.saved_snapshot = self._snapshot()
            self.status.set("Enregistré : " + self.current_path)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Enregistrement impossible", str(exc))
    def export_as_svg(self):
        path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("Image vectorielle SVG", "*.svg")])
        if not path:
            return
        try:
            export_svg(path, self.document)
            self.status.set("SVG exporté : " + path)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Export impossible", str(exc))
    def store_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".ovjson", filetypes=[("OpenVisio", "*.ovjson")])
        if path:
            previous_path = self.current_path
            self.current_path = path
            self.store()
            if self._snapshot() != self.saved_snapshot:
                self.current_path = previous_path

def main():
    Editor().mainloop()
