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
from .viewport import Viewport
from .layout import snap, align, distribute, move_group
from .clipboard import copy_selection, paste_selection
from .templates import TEMPLATES, create_template
from .selection import nodes_in_rectangle
from .selection_state import select_node, select_rectangle, reconcile_selection
from .property_commands import update_equipment, update_connection
from .shortcut_policy import editor_shortcut_allowed
from .search import find_nodes
from .commands import add_equipment, remove_selection, connect_equipment

class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenVisio 42.0 — Python natif")
        self.geometry("1100x720")
        self.document = {"nodes": [], "edges": []}
        self.current_path = None
        self.selected = None
        self.selected_edge = None
        self.selected_nodes = set()
        self.grid_enabled = True
        self.snap_enabled = True
        self.link_start = None
        self.viewport = Viewport()
        self._pan_anchor = None
        self._drag_anchor = None
        self._marquee_start = None
        self._marquee_end = None
        self._marquee_previous = set()
        self._clipboard = None
        self._paste_count = 0
        self.history = History(self.document)
        self.saved_snapshot = self._snapshot()
        self.protocol("WM_DELETE_WINDOW", self.close_safely)
        self.canvas = tk.Canvas(self, bg="#f8fafc", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-3>", self.show_context_menu)
        self.canvas.bind("<Double-Button-1>", self.add_node)
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        self.canvas.bind("<Configure>", lambda event: self.draw())
        self.canvas.bind("<MouseWheel>", self.wheel_zoom)
        self.canvas.bind("<Button-4>", lambda event: self.zoom_at(event, 1.12))
        self.canvas.bind("<Button-5>", lambda event: self.zoom_at(event, 1/1.12))
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan_motion)
        self.canvas.bind("<ButtonRelease-2>", lambda event: self.end_pan())
        bar = tk.Menu(self)
        filemenu = tk.Menu(bar, tearoff=False)
        for label, command in [("Nouveau", self.new), ("Ouvrir", self.open), ("Enregistrer", self.store), ("Enregistrer sous", self.store_as), ("Exporter en SVG", self.export_as_svg)]:
            filemenu.add_command(label=label, command=command)
        bar.add_cascade(label="Fichier", menu=filemenu)
        edit = tk.Menu(bar, tearoff=False)
        edit.add_command(label="Annuler", command=self.undo)
        edit.add_command(label="Rétablir", command=self.redo)
        edit.add_separator()
        edit.add_command(label="Copier", command=self.copy_selected)
        edit.add_command(label="Coller", command=self.paste_selected)
        edit.add_command(label="Dupliquer", command=self.duplicate_selected)
        edit.add_command(label="Rechercher un équipement", command=self.find_equipment)
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
        templates_menu = tk.Menu(bar, tearoff=False)
        for template_name in TEMPLATES:
            templates_menu.add_command(label=template_name, command=lambda name=template_name: self.load_template(name))
        bar.add_cascade(label="Modèles", menu=templates_menu)
        view = tk.Menu(bar, tearoff=False)
        view.add_command(label="Ajuster à la fenêtre", command=self.fit_view)
        view.add_command(label="Zoom +", command=lambda: self.zoom_center(1.2))
        view.add_command(label="Zoom -", command=lambda: self.zoom_center(1/1.2))
        view.add_command(label="Zoom 100 %", command=self.reset_view)
        view.add_separator()
        view.add_command(label="Afficher / masquer la grille", command=self.toggle_grid)
        view.add_command(label="Activer / désactiver l'accrochage", command=self.toggle_snap)
        view.add_command(label="Aligner horizontalement", command=lambda: self.align_selection("y"))
        view.add_command(label="Aligner verticalement", command=lambda: self.align_selection("x"))
        view.add_command(label="Distribuer horizontalement", command=lambda: self.distribute_selection("x"))
        view.add_command(label="Distribuer verticalement", command=lambda: self.distribute_selection("y"))
        bar.add_cascade(label="Affichage", menu=view)
        self.config(menu=bar)
        toolbar = tk.Frame(self, bg="#e8eef6", padx=8, pady=6)
        toolbar.pack(side="top", fill="x", before=self.canvas)
        actions = (
            ("Nouveau", self.new), ("Ouvrir", self.open), ("Enregistrer", self.store),
            ("Annuler", self.undo), ("Rétablir", self.redo),
            ("Ajouter serveur", lambda: self.create_node(*self.viewport.world(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2))),
            ("Relier", self.begin_link), ("Propriétés", self.edit_properties),
            ("Rechercher", self.find_equipment), ("Ajuster", self.fit_view),
        )
        for label, command in actions:
            tk.Button(toolbar, text=label, command=command, padx=8, pady=3).pack(side="left", padx=2)
        shortcuts = (
            ("<Control-f>", self.find_equipment),
            ("<Control-a>", self.select_all),
            ("<Escape>", self.clear_selection),
            ("<Control-c>", self.copy_selected),
            ("<Control-v>", self.paste_selected),
            ("<Control-d>", self.duplicate_selected),
            ("<Control-z>", self.undo),
            ("<Control-y>", self.redo),
            ("<Control-s>", self.store),
            ("<Control-o>", self.open),
            ("<Delete>", self.delete_selected),
            ("<F2>", self.edit_properties),
        )
        for sequence, command in shortcuts:
            self.bind(sequence, lambda event, action=command: self._editor_shortcut(event, action))
        self.status = tk.StringVar(value="Double-clic : ajouter | Glisser : déplacer | Édition : relier")
        tk.Label(self, textvariable=self.status, anchor="w").pack(fill="x")
    def _editor_shortcut(self, event, action):
        """Never intercept text editing or modal dialog keystrokes."""
        if not editor_shortcut_allowed(event.widget.winfo_class(), event.widget.winfo_toplevel() is self):
            return None
        action()
        return "break"

    def show_context_menu(self, event):
        """Context actions follow the object under the pointer."""
        node = self.node_at(event.x, event.y)
        edge = None if node else self.edge_at(event.x, event.y)
        if node is not None:
            if node["id"] not in self.selected_nodes:
                self.selected_nodes = {node["id"]}
            self.selected = node["id"]
            self.selected_edge = None
        elif edge is not None:
            self.selected_nodes.clear()
            self.selected = None
            self.selected_edge = edge["id"]
        else:
            self.selected_nodes.clear()
            self.selected = None
            self.selected_edge = None
        self.draw()
        menu = tk.Menu(self, tearoff=False)
        if node is not None:
            menu.add_command(label="Propriétés de l'équipement", command=self.edit_properties)
            menu.add_command(label="Créer une liaison", command=self.begin_link)
            menu.add_command(label="Dupliquer", command=self.duplicate_selected)
            menu.add_separator()
            menu.add_command(label="Supprimer", command=self.delete_selected)
        elif edge is not None:
            menu.add_command(label="Propriétés de la liaison", command=self.edit_selected_link)
            menu.add_command(label="Supprimer la liaison", command=self.delete_selected)
        else:
            x, y = self.viewport.world(event.x, event.y)
            menu.add_command(label="Ajouter un serveur ici", command=lambda: self.create_node(x, y))
            menu.add_command(label="Coller", command=self.paste_selected)
            menu.add_command(label="Ajuster à la fenêtre", command=self.fit_view)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def load_template(self, name):
        if not self._confirm_discard():
            return
        self.document = create_template(name)
        self.current_path = None
        self.selected = None
        self.selected_edge = None
        self.selected_nodes.clear()
        self.link_start = None
        self.history.reset(self.document)
        self.saved_snapshot = json.dumps({"nodes": [], "edges": []}, sort_keys=True, ensure_ascii=False)
        self.fit_view()
        self.status.set("Modèle chargé : " + name + " — Enregistrez pour conserver votre diagramme")
    def find_equipment(self):
        query = simpledialog.askstring("Rechercher", "Nom, hôte, IP, constructeur, modèle ou type :", parent=self)
        if query is None:
            return
        matches = find_nodes(self.document["nodes"], query)
        if not matches:
            self.status.set("Aucun équipement trouvé pour : " + query)
            return
        self.selected_nodes = {node["id"] for node in matches}
        self.selected = matches[0]["id"] if len(matches) == 1 else None
        self.selected_edge = None
        self.viewport.fit(matches, self.canvas.winfo_width(), self.canvas.winfo_height())
        self.status.set(str(len(matches)) + " équipement(s) trouvé(s) pour : " + query)
        self.draw()
    def select_all(self):
        self.selected_nodes = {n["id"] for n in self.document["nodes"]}
        self.selected = None
        self.selected_edge = None
        self.draw()
    def clear_selection(self):
        self.selected_nodes.clear()
        self.selected = None
        self.selected_edge = None
        self.draw()
    def copy_selected(self):
        ids = self.selected_nodes or ({self.selected} if self.selected else set())
        self._clipboard = copy_selection(self.document, ids)
        self._paste_count = 0
    def paste_selected(self):
        if not self._clipboard or not self._clipboard["nodes"]:
            return
        self._paste_count += 1
        self.selected_nodes = paste_selection(self.document, self._clipboard, offset=40*self._paste_count)
        self.selected = next(iter(self.selected_nodes), None)
        self.selected_edge = None
        self._record_change()
        self.draw()
    def duplicate_selected(self):
        self.copy_selected()
        self.paste_selected()
    def toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        self.draw()
    def toggle_snap(self):
        self.snap_enabled = not self.snap_enabled
        self.status.set("Accrochage " + ("activé" if self.snap_enabled else "désactivé"))
    def align_selection(self, axis):
        if align(self.document["nodes"], self.selected_nodes, axis):
            self._record_change()
            self.draw()
        else:
            messagebox.showinfo("Alignement", "Sélectionnez au moins deux équipements avec Ctrl+clic")
    def distribute_selection(self, axis):
        if distribute(self.document["nodes"], self.selected_nodes, axis):
            self._record_change()
            self.draw()
        else:
            messagebox.showinfo("Distribution", "Sélectionnez au moins trois équipements avec des positions différentes")
    def end_drag(self, event):
        if self._marquee_start is not None and self._marquee_end is not None:
            x0, y0 = self._marquee_start
            x1, y1 = self._marquee_end
            if abs(x1-x0) >= 4 or abs(y1-y0) >= 4:
                ids = nodes_in_rectangle(self.document["nodes"], x0, y0, x1, y1)
                self.selected_nodes = select_rectangle(self._marquee_previous, ids, additive=bool(event.state & 0x0001))
                self.selected = next(iter(self.selected_nodes), None) if len(self.selected_nodes)==1 else None
                self.selected_edge = None
        self._marquee_start = self._marquee_end = None
        self._marquee_previous.clear()
        self._drag_anchor = None
        self._record_change()
        self.draw()
    def zoom_at(self, event, factor):
        self.viewport.zoom_at(factor, event.x, event.y)
        self.draw()
    def wheel_zoom(self, event):
        self.zoom_at(event, 1.12 if event.delta > 0 else 1/1.12)
    def zoom_center(self, factor):
        self.viewport.zoom_at(factor, self.canvas.winfo_width()/2, self.canvas.winfo_height()/2)
        self.draw()
    def reset_view(self):
        self.viewport = Viewport()
        self.draw()
    def fit_view(self):
        self.viewport.fit(self.document["nodes"], self.canvas.winfo_width(), self.canvas.winfo_height())
        self.draw()
    def start_pan(self, event):
        self._pan_anchor = (event.x, event.y)
    def pan_motion(self, event):
        if self._pan_anchor is not None:
            x, y = self._pan_anchor
            self.viewport.pan(event.x-x, event.y-y)
            self._pan_anchor = (event.x, event.y)
            self.draw()
    def end_pan(self):
        self._pan_anchor = None
    def _record_change(self):
        self.history.record(self.document)
        self.selected_nodes, self.selected, self.selected_edge = reconcile_selection(
            self.document, self.selected_nodes, self.selected, self.selected_edge
        )
        if self.link_start not in {node["id"] for node in self.document["nodes"]}:
            self.link_start = None
    def undo(self):
        document = self.history.undo()
        if document is not None:
            self.document = document
            self.selected = self.selected_edge = None
            self.selected_nodes.clear()
            self.link_start = None
            self.draw()
    def redo(self):
        document = self.history.redo()
        if document is not None:
            self.document = document
            self.selected = self.selected_edge = None
            self.selected_nodes.clear()
            self.link_start = None
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
        self.selected_nodes.clear()
        self.saved_snapshot = self._snapshot()
        self.history.reset(self.document)
        self.draw()
    def create_node(self, x, y, kind="server"):
        self.document, node_id = add_equipment(self.document, x, y, kind)
        self._record_change()
        self.selected = node_id
        self.selected_nodes = {node_id}
        self.draw()
    def add_node(self, event):
        self.create_node(*self.viewport.world(event.x, event.y))
    def node_at(self, x, y):
        return node_at(self.document["nodes"], *self.viewport.world(x, y))
    def edge_at(self, x, y):
        return edge_at(self.document["nodes"], self.document["edges"], *self.viewport.world(x, y), tolerance=9/self.viewport.zoom)
    def click(self, event):
        node = self.node_at(event.x, event.y)
        self._marquee_previous = set(self.selected_nodes)
        if self.link_start is not None and node is not None:
            if node["id"] != self.link_start:
                try:
                    self.document = connect_equipment(self.document, self.link_start, node["id"])
                    self._record_change()
                except ValueError as exc:
                    self.status.set(str(exc))
            self.link_start = None
        if node is None and (event.state & 0x0001):
            # Preserve existing selection until additive marquee completes.
            self.selected = None
        else:
            self.selected_nodes, self.selected = select_node(
                self.selected_nodes, node["id"] if node else None,
                ctrl=bool(event.state & 0x0004),
            )
        self.selected_edge = None if node else (self.edge_at(event.x, event.y) or {}).get("id")
        self._drag_anchor = self.viewport.world(event.x, event.y) if node and not (event.state & 0x0004) else None
        self._marquee_start = self.viewport.world(event.x, event.y) if node is None and self.selected_edge is None else None
        self._marquee_end = None
        self.draw()
    def drag(self, event):
        if self._marquee_start is not None:
            self._marquee_end = self.viewport.world(event.x, event.y)
            self.draw()
            return
        if self._drag_anchor is None or not self.selected_nodes:
            return
        x, y = self.viewport.world(event.x, event.y)
        old_x, old_y = self._drag_anchor
        dx, dy = x - old_x, y - old_y
        changed = move_group(self.document["nodes"], self.selected_nodes, dx, dy, 20 if self.snap_enabled else None)
        if changed:
            self._drag_anchor = (x, y) if not self.snap_enabled else (old_x + snap(dx), old_y + snap(dy))
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
        property_fields = (
            ("label", "Nom"), ("hostname", "Hôte / FQDN"), ("address", "Adresse IP"),
            ("vendor", "Constructeur"), ("model", "Modèle"), ("role", "Rôle"),
            ("location", "Site / emplacement"), ("serial_number", "Numéro de série"),
            ("firmware", "Firmware"), ("notes", "Notes"),
        )
        for row, (key, title) in enumerate(property_fields):
            tk.Label(dialog, text=title, anchor="w").grid(row=row, column=0, padx=12, pady=5, sticky="w")
            value = tk.StringVar(value=node.get(key, ""))
            if key == "notes":
                entry = tk.Text(dialog, width=40, height=3, wrap="word")
                entry.insert("1.0", value.get())
                entry.grid(row=row, column=1, padx=12, pady=5, sticky="ew")
                fields[key] = entry
            else:
                tk.Entry(dialog, textvariable=value, width=42).grid(row=row, column=1, padx=12, pady=5)
                fields[key] = value
        shape_row = len(property_fields)
        tk.Label(dialog, text="Type de forme", anchor="w").grid(row=shape_row, column=0, padx=12, pady=5, sticky="w")
        shape = tk.StringVar(value=node.get("shape", "server"))
        tk.OptionMenu(dialog, shape, *SHAPES.keys()).grid(row=shape_row, column=1, padx=12, pady=5, sticky="ew")
        def apply():
            try:
                raw = {key: (value.get("1.0", "end-1c") if key == "notes" else value.get()) for key, value in fields.items()}
                updated_document = update_equipment(self.document, node["id"], raw, shape.get())
            except ValueError as exc:
                messagebox.showerror("Propriétés invalides", str(exc), parent=dialog)
                return
            self.document = updated_document
            self._record_change()
            self.draw()
            dialog.destroy()
        tk.Button(dialog, text="Enregistrer", command=apply).grid(row=shape_row+1, column=1, pady=12, sticky="e")
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
                updated_document = update_connection(
                    self.document, edge["id"], {key: value.get() for key, value in fields.items()}
                )
                self.document = updated_document
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
        ids = set(self.selected_nodes)
        if self.selected:
            ids.add(self.selected)
        selected_edge = self.selected_edge
        if not ids and not selected_edge:
            return
        self.document = remove_selection(self.document, ids, selected_edge)
        self.selected = None
        self.selected_edge = None
        self.selected_nodes.clear()
        self._record_change()
        self.draw()
    def draw(self):
        draw_document(self.canvas, self.document, self.selected, self.selected_edge, self.viewport, grid=self.grid_enabled, selected_nodes=self.selected_nodes)
        if self._marquee_start is not None and self._marquee_end is not None:
            x0, y0 = self.viewport.screen(*self._marquee_start)
            x1, y1 = self.viewport.screen(*self._marquee_end)
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="#2563eb", dash=(5, 3), width=2)
    def open(self):
        path = filedialog.askopenfilename(filetypes=[("OpenVisio JSON", "*.ovjson *.json")])
        if not path:
            return
        try:
            document = load(path)
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror("Ouverture impossible", str(exc))
            return
        if not self._confirm_discard():
            return
        # Commit the validated document only after user confirmation.
        self.history.reset(document)
        self.document = document
        self.current_path = path
        self.selected = None
        self.selected_edge = None
        self.selected_nodes.clear()
        self.link_start = None
        self.saved_snapshot = self._snapshot()
        self.draw()
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
        if not path:
            return
        try:
            save(path, self.document)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Enregistrement impossible", str(exc))
            return
        self.current_path = path
        self.saved_snapshot = self._snapshot()
        self.status.set("Enregistré : " + path)

def main():
    Editor().mainloop()
