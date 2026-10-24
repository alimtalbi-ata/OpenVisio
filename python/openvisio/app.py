"""Native Tkinter diagram editor. Author: Abdelhalim Talbi."""
import tkinter as tk
import json
from tkinter import filedialog, messagebox, simpledialog
from uuid import uuid4
from pathlib import Path
from . import __version__
from .model import load, save, SaveConflict
from .save_diagnostics import save_with_diagnostics, display_save_diagnostics
from .autosave import (digest_file, write_journal, list_journals, discard_journal, RecoveryConflict)
from .unsaved_recovery import UntitledSession, recoverable_sessions, discard_session
from .saved_recovery_lock import SavedJournalLease
from .document_recovery import backup_path, read_backup
from .document_transactions import replace_document
from .document_service import (open_document, open_document_with_revision,
                               save_document, save_document_with_revision,
                               restore_previous, inspect_previous, restore_inspected)
from .export import export_svg
from .vsdx import import_vsdx, export_vsdx, VsdxExternalChangesError
from .shapes import SHAPES, get_shape
from .properties import normalize_properties
from .links import normalize_link, PROTOCOLS
from .history import History
from .render import node_at, edge_at, resolve_hit
from .retained_canvas import RetainedCanvasRenderer
from .routing import set_edge_routing, RoutingError
from .viewport import Viewport
from .layout import snap, align, distribute, move_group
from .layers import (create_layer, assign_nodes, set_visibility, set_locked,
                     rename_layer, delete_layer, project_visible, project_editable)
from .clipboard import copy_selection, paste_selection
from .templates import TEMPLATES, create_template
from .selection import nodes_in_rectangle
from .selection_state import select_node, select_rectangle, reconcile_selection
from .property_commands import update_equipment, update_connection
from .shortcut_policy import editor_shortcut_allowed
from .context_actions import context_selection
from .editor_state import document_summary, document_dirty
from .search import find_nodes
from .commands import add_equipment, remove_selection, connect_equipment
from .group_commands import group_members, group_selection, ungroup_selection, resize_group

class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"OpenVisio {__version__} — Python natif")
        self.geometry("1100x720")
        self.document = {"nodes": [], "edges": []}
        self.current_path = None
        self._saved_disk_digest = None
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
        self._saved_disk_digest = None
        self._autosave_warning = False
        self._destroying = False
        self._autosave_after_id = None
        self._startup_recovery_after_id = None
        self._saved_journal_id = uuid4().hex
        self._saved_lease = None
        try:
            self._untitled_session = UntitledSession()
        except (OSError, ValueError) as exc:
            self._untitled_session = None
            self._untitled_recovery_error = str(exc)
        else:
            self._untitled_recovery_error = None
        self.protocol("WM_DELETE_WINDOW", self.close_safely)
        self.canvas = tk.Canvas(self, bg="#f8fafc", highlightthickness=0)
        self._canvas_renderer = RetainedCanvasRenderer(self.canvas)
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
        for label, command in [("Nouveau", self.new), ("Ouvrir", self.open), ("Enregistrer", self.store), ("Enregistrer sous", self.store_as), ("Exporter en SVG", self.export_as_svg), ("Importer Visio VSDX (expérimental)", self.import_from_vsdx), ("Exporter Visio VSDX (expérimental)", self.export_as_vsdx)]:
            filemenu.add_command(label=label, command=command)
        filemenu.add_separator()
        filemenu.add_command(label="Restaurer la sauvegarde précédente (.bak)", command=self.restore_backup)
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
        edit.add_command(label="Ajouter un chemin SAN parallèle (ports distincts)", command=self.add_parallel_link)
        edit.add_command(label="Basculer le routage orthogonal de la liaison", command=self.toggle_selected_edge_routing)
        edit.add_command(label="Grouper la sélection (Ctrl+G)", command=self.group_selected)
        edit.add_command(label="Dissocier les groupes (Ctrl+Maj+G)", command=self.ungroup_selected)
        edit.add_command(label="Redimensionner le groupe", command=self.resize_selected_group)
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
        layers_menu = tk.Menu(bar, tearoff=False, postcommand=self._refresh_layer_menus)
        layers_menu.add_command(label="Créer un calque...", command=self.new_layer)
        self.assign_layer_menu = tk.Menu(layers_menu, tearoff=False)
        self.visibility_layer_menu = tk.Menu(layers_menu, tearoff=False)
        self.lock_layer_menu = tk.Menu(layers_menu, tearoff=False)
        self.rename_layer_menu = tk.Menu(layers_menu, tearoff=False)
        self.delete_layer_menu = tk.Menu(layers_menu, tearoff=False)
        layers_menu.add_cascade(label="Affecter la sélection", menu=self.assign_layer_menu)
        layers_menu.add_cascade(label="Afficher / masquer", menu=self.visibility_layer_menu)
        layers_menu.add_cascade(label="Verrouiller / déverrouiller", menu=self.lock_layer_menu)
        layers_menu.add_cascade(label="Renommer", menu=self.rename_layer_menu)
        layers_menu.add_cascade(label="Supprimer sans effacer les objets", menu=self.delete_layer_menu)
        bar.add_cascade(label="Calques", menu=layers_menu)
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
            ("<Control-g>", self.group_selected),
            ("<Control-Shift-G>", self.ungroup_selected),
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
        self.document_status = tk.StringVar()
        tk.Label(self, textvariable=self.document_status, anchor="w", bg="#e8eef6").pack(fill="x")
        self._refresh_document_status()
        self._autosave_after_id = self.after(30_000, self._autosave_tick)
        self._startup_recovery_after_id = self.after(250, self._offer_untitled_recovery)
    def _switch_saved_lease(self, path):
        """Keep a per-session lock while this editor owns a saved document."""
        if path is not None and self._saved_lease is not None and self._saved_lease.owns(path, self._saved_journal_id):
            return
        new_lease = SavedJournalLease(path, self._saved_journal_id) if path else None
        old_lease = self._saved_lease
        self._saved_lease = new_lease
        if old_lease is not None:
            old_lease.close()

    def _autosave_tick(self):
        """Persist dirty saved and untitled diagrams without modifying originals."""
        pending = self._autosave_after_id
        self._autosave_after_id = None
        if pending is not None:
            try:
                self.after_cancel(pending)
            except tk.TclError:
                pass  # A callback invoked by Tk has already been dequeued.
        if self._destroying:
            return
        try:
            if (self.current_path and self._saved_disk_digest is not None
                    and self._snapshot() != self.saved_snapshot):
                if self._saved_lease is None or not self._saved_lease.owns(self.current_path, self._saved_journal_id):
                    raise ValueError("Verrou de récupération indisponible")
                write_journal(self.current_path, self.document, self._saved_disk_digest,
                              session_id=self._saved_journal_id)
                self._autosave_warning = False
            elif self.current_path is None and self._untitled_session is not None:
                if self._snapshot() != self.saved_snapshot:
                    self._untitled_session.write(self.document)
                else:
                    self._untitled_session.discard()
                self._autosave_warning = False
        except (OSError, ValueError) as exc:
            if not self._autosave_warning:
                self.status.set("Récupération automatique suspendue : " + str(exc))
                self._autosave_warning = True
        finally:
            if not self._destroying:
                self._autosave_after_id = self.after(30_000, self._autosave_tick)
    def _offer_untitled_recovery(self):
        """Offer abandoned untitled work on startup; never overwrite a native file."""
        pending = self._startup_recovery_after_id
        self._startup_recovery_after_id = None
        if pending is not None:
            try:
                self.after_cancel(pending)
            except tk.TclError:
                pass
        if self._destroying or self.current_path is not None:
            return  # An Explorer-opened saved document must not be replaced by untitled recovery.
        if self._snapshot() != self.saved_snapshot:
            return  # Never replace edits made before the startup prompt.
        candidates, warnings = recoverable_sessions()
        if warnings:
            self.status.set("Récupération : " + "; ".join(warnings[:2]))
        for entry in candidates:
            answer = messagebox.askyesnocancel(
                "Diagramme sans titre récupérable",
                "Un diagramme jamais enregistré a été retrouvé (" +
                str(len(entry["document"]["nodes"])) + " équipements).\n"
                "Oui : récupérer en mémoire ; Non : supprimer le journal ; "
                "Annuler : le conserver pour plus tard.", parent=self)
            if answer is None:
                return
            if not answer:
                try:
                    discard_session(entry["path"].parent, entry["session"])
                except (OSError, ValueError) as exc:
                    self.status.set("Récupération non supprimée : " + str(exc))
                    return
                continue
            # Transfer to the active session before removing the old journal.
            if self._untitled_session is None:
                messagebox.showerror("Récupération indisponible",
                                     self._untitled_recovery_error or "Journal inaccessible", parent=self)
                return
            try:
                self._untitled_session.write(entry["document"])
            except (OSError, ValueError) as exc:
                messagebox.showerror("Récupération impossible", str(exc), parent=self)
                return
            self.document = entry["document"]
            self.history.reset(self.document)
            self.current_path = None
            self._saved_disk_digest = None
            self.saved_snapshot = json.dumps({"nodes": [], "edges": []}, sort_keys=True, ensure_ascii=False)
            self.selected = self.selected_edge = None
            self.selected_nodes.clear()
            self.link_start = None
            try:
                discard_session(entry["path"].parent, entry["session"])
            except (OSError, ValueError):
                pass  # New journal already holds the recovered document.
            self.draw()
            self.status.set("Diagramme sans titre récupéré en mémoire — Enregistrez-le")
            return

    def _discard_untitled(self):
        if self._untitled_session is not None:
            self._untitled_session.discard()

    def _refresh_document_status(self):
        """Present unsaved state and selection without hiding action feedback."""
        dirty = document_dirty(self._snapshot(), self.saved_snapshot)
        self.title(f"OpenVisio {__version__} — " + ("* " if dirty else "") + (str(self.current_path) if self.current_path else "Sans titre"))
        summary = document_summary(
            self.document, self.selected_nodes, self.selected_edge, dirty, self.current_path
        )
        visible_count = len(project_visible(self.document)["nodes"])
        if visible_count != len(self.document["nodes"]):
            summary += f" | {visible_count}/{len(self.document['nodes'])} visibles"
        self.document_status.set(summary)

    def _editor_shortcut(self, event, action):
        """Never intercept text editing or modal dialog keystrokes."""
        if not editor_shortcut_allowed(event.widget.winfo_class(), event.widget.winfo_toplevel() is self):
            return None
        action()
        return "break"

    def show_context_menu(self, event):
        """Context actions follow the object under the pointer."""
        node = self.node_at(event.x, event.y)
        edge = (None if node is not None and node.get("shape") != "visio-group"
                else self.edge_at(event.x, event.y))
        node, edge = resolve_hit(node, edge)
        self.selected_nodes, self.selected, self.selected_edge = context_selection(
            node["id"] if node is not None else None,
            edge["id"] if edge is not None else None,
            self.selected_nodes,
        )
        self.draw()
        menu = tk.Menu(self, tearoff=False)
        if node is not None:
            menu.add_command(label="Propriétés de l'équipement", command=self.edit_properties)
            menu.add_command(label="Créer une liaison", command=self.begin_link)
            menu.add_command(label="Dupliquer", command=self.duplicate_selected)
            if node.get("shape") == "visio-group":
                menu.add_command(label="Dissocier le groupe", command=self.ungroup_selected)
                menu.add_command(label="Redimensionner le groupe", command=self.resize_selected_group)
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
        try:
            document = create_template(name)
            # Validate and snapshot before asking to discard existing edits.
            candidate = History(document, limit=self.history.limit)
        except (ValueError, KeyError, TypeError) as exc:
            messagebox.showerror("Modèle invalide", str(exc))
            return
        if not self._confirm_discard():
            return
        self.document = candidate.current
        self.history = candidate
        self._switch_saved_lease(None)
        self.current_path = None
        self._saved_disk_digest = None
        self.selected = None
        self.selected_edge = None
        self.selected_nodes.clear()
        self.link_start = None
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
        self.selected_nodes = {n["id"] for n in project_editable(self.document)["nodes"]}
        self.selected = None
        self.selected_edge = None
        self.draw()
    def clear_selection(self):
        """Escape also cancels a pending connection operation."""
        self.selected_nodes.clear()
        self.selected = None
        self.selected_edge = None
        self.link_start = None
        self.status.set("Sélection et création de liaison annulées")
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
    def _refresh_layer_menus(self):
        self.assign_layer_menu.delete(0, "end")
        self.visibility_layer_menu.delete(0, "end")
        self.lock_layer_menu.delete(0, "end")
        self.rename_layer_menu.delete(0, "end")
        self.delete_layer_menu.delete(0, "end")
        layers = self.document.get("layers", [])
        self.assign_layer_menu.add_command(
            label="Aucun calque", command=lambda: self.assign_selection_layer(None))
        for layer in layers:
            lid = layer["id"]
            label = layer.get("name", lid)
            self.assign_layer_menu.add_command(
                label=label, command=lambda ident=lid: self.assign_selection_layer(ident))
            prefix = "✓ " if layer.get("visible", True) else "○ "
            self.visibility_layer_menu.add_command(
                label=prefix + label, command=lambda ident=lid: self.toggle_layer_visibility(ident))
            locked_label = ("🔒 " if layer.get("locked", False) else "○ ") + label
            self.lock_layer_menu.add_command(
                label=locked_label, command=lambda ident=lid: self.toggle_layer_lock(ident))
            self.rename_layer_menu.add_command(
                label=label, command=lambda ident=lid: self.rename_existing_layer(ident))
            self.delete_layer_menu.add_command(
                label=label, command=lambda ident=lid: self.delete_existing_layer(ident))
        if not layers:
            self.visibility_layer_menu.add_command(label="Aucun calque", state="disabled")
            for menu in (self.lock_layer_menu, self.rename_layer_menu, self.delete_layer_menu):
                menu.add_command(label="Aucun calque", state="disabled")

    def new_layer(self):
        name = simpledialog.askstring("Nouveau calque", "Nom du calque :", parent=self)
        if name is None:
            return
        try:
            self.document, layer_id = create_layer(self.document, name)
        except ValueError as exc:
            messagebox.showerror("Calque", str(exc), parent=self)
            return
        self._record_change()
        self.status.set("Calque créé : " + name.strip())
        self.draw()

    def assign_selection_layer(self, layer_id):
        editable = {n["id"] for n in project_editable(self.document)["nodes"]}
        selected = set(self.selected_nodes) & editable
        if selected and not group_members(self.document["nodes"], selected).issubset(editable):
            self.status.set("Changement de calque refusé : membre verrouillé ou masqué")
            return
        if not selected:
            messagebox.showinfo("Calques", "Sélectionnez des équipements modifiables.", parent=self)
            return
        try:
            self.document = assign_nodes(self.document, selected, layer_id)
        except ValueError as exc:
            messagebox.showerror("Calques", str(exc), parent=self)
            return
        editable_now = {n["id"] for n in project_editable(self.document)["nodes"]}
        self.selected_nodes.intersection_update(editable_now)
        if self.selected not in editable_now:
            self.selected = None
        self._record_change()
        self.draw()

    def toggle_layer_lock(self, layer_id):
        layer = next((item for item in self.document.get("layers", []) if item["id"] == layer_id), None)
        if layer is None:
            return
        self.document = set_locked(self.document, layer_id, not layer.get("locked", False))
        self._record_change()
        editable = project_editable(self.document)
        self.selected_nodes.intersection_update({n["id"] for n in editable["nodes"]})
        if self.selected not in {n["id"] for n in editable["nodes"]}:
            self.selected = None
        if self.selected_edge not in {e["id"] for e in editable["edges"]}:
            self.selected_edge = None
        if self.link_start not in {n["id"] for n in editable["nodes"]}:
            self.link_start = None
        self.status.set("Calque " + ("verrouillé" if not layer.get("locked", False) else "déverrouillé"))
        self.draw()

    def rename_existing_layer(self, layer_id):
        layer = next((item for item in self.document.get("layers", []) if item["id"] == layer_id), None)
        if layer is None:
            return
        name = simpledialog.askstring("Renommer le calque", "Nouveau nom :", initialvalue=layer.get("name", ""), parent=self)
        if name is None:
            return
        try:
            self.document = rename_layer(self.document, layer_id, name)
        except ValueError as exc:
            messagebox.showerror("Calque invalide", str(exc), parent=self)
            return
        self._record_change()
        self.draw()

    def delete_existing_layer(self, layer_id):
        layer = next((item for item in self.document.get("layers", []) if item["id"] == layer_id), None)
        if layer is None:
            return
        if not messagebox.askyesno("Supprimer le calque",
                                   "Supprimer le calque « " + layer.get("name", layer_id) + " » ?\n"
                                   "Les équipements et les connexions seront conservés et deviendront sans calque.", parent=self):
            return
        try:
            self.document = delete_layer(self.document, layer_id)
        except ValueError as exc:
            messagebox.showerror("Suppression refusée", str(exc), parent=self)
            return
        self._record_change()
        self.draw()

    def toggle_layer_visibility(self, layer_id):
        layer = next((l for l in self.document.get("layers", []) if l["id"] == layer_id), None)
        if layer is None:
            return
        self.document = set_visibility(self.document, layer_id, not layer.get("visible", True))
        editable = {n["id"] for n in project_editable(self.document)["nodes"]}
        self.selected_nodes.intersection_update(editable)
        if self.selected not in editable:
            self.selected = None
        if self.selected_edge not in {e["id"] for e in project_editable(self.document)["edges"]}:
            self.selected_edge = None
        self.link_start = None
        self._record_change()
        self.draw()

    def toggle_grid(self):
        self.grid_enabled = not self.grid_enabled
        self.draw()
    def toggle_snap(self):
        self.snap_enabled = not self.snap_enabled
        self.status.set("Accrochage " + ("activé" if self.snap_enabled else "désactivé"))
    def _editable_layout_selection(self):
        """Do not translate hidden/locked descendants through their parent."""
        editable_ids = {n["id"] for n in project_editable(self.document)["nodes"]}
        selected = set(self.selected_nodes)
        if not selected or not group_members(self.document["nodes"], selected).issubset(editable_ids):
            self.status.set("Alignement/distribution refusé : membre verrouillé ou masqué")
            return None
        return selected

    def align_selection(self, axis):
        selected = self._editable_layout_selection()
        if selected is None:
            return
        if align(self.document["nodes"], selected, axis):
            self._record_change()
            self.draw()
        else:
            messagebox.showinfo("Alignement", "Sélectionnez au moins deux équipements avec Ctrl+clic")

    def distribute_selection(self, axis):
        selected = self._editable_layout_selection()
        if selected is None:
            return
        if distribute(self.document["nodes"], selected, axis):
            self._record_change()
            self.draw()
        else:
            messagebox.showinfo("Distribution", "Sélectionnez au moins trois équipements avec des positions différentes")
    def end_drag(self, event):
        if self._marquee_start is not None and self._marquee_end is not None:
            x0, y0 = self._marquee_start
            x1, y1 = self._marquee_end
            if abs(x1-x0) >= 4 or abs(y1-y0) >= 4:
                ids = nodes_in_rectangle(project_editable(self.document)["nodes"], x0, y0, x1, y1)
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
        self.viewport.fit(project_visible(self.document)["nodes"], self.canvas.winfo_width(), self.canvas.winfo_height())
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
    def _restore_history_document(self, document, action):
        """Centralize selection cleanup after undo/redo."""
        if document is None:
            self.status.set("Aucune opération à " + action.lower())
            return
        self.document = document
        self.selected = self.selected_edge = None
        self.selected_nodes.clear()
        self.link_start = None
        self._drag_anchor = None
        self._marquee_start = self._marquee_end = None
        self.status.set(action + " effectué")
        self.draw()

    def undo(self):
        self._restore_history_document(self.history.undo(), "Annulation")

    def redo(self):
        self._restore_history_document(self.history.redo(), "Rétablissement")
    def _snapshot(self):
        return json.dumps(self.document, sort_keys=True, ensure_ascii=False)
    def _confirm_discard(self):
        if self._snapshot() == self.saved_snapshot:
            if self.current_path is None:
                try:
                    self._discard_untitled()
                except (OSError, ValueError) as exc:
                    messagebox.showerror("Récupération", str(exc), parent=self)
                    return False
            return True
        answer = messagebox.askyesnocancel("Modifications non enregistrées", "Enregistrer les modifications avant de continuer ?", parent=self)
        if answer is None:
            return False
        if answer:
            self.store()
            return self._snapshot() == self.saved_snapshot
        try:
            if self.current_path:
                discard_journal(self.current_path, session_id=self._saved_journal_id, lease=self._saved_lease)
            else:
                self._discard_untitled()
        except (OSError, ValueError) as exc:
            messagebox.showerror("Récupération", str(exc), parent=self)
            return False
        return True
    def destroy(self):
        self._destroying = True
        # Tk registers Python callbacks by command name. Destroying a root with
        # pending after callbacks leaves invalid Tcl commands in later Tk roots.
        for attr in ("_autosave_after_id", "_startup_recovery_after_id"):
            callback_id = getattr(self, attr, None)
            if callback_id is not None:
                try:
                    self.after_cancel(callback_id)
                except tk.TclError:
                    pass
                setattr(self, attr, None)
        if getattr(self, "_saved_lease", None) is not None:
            self._switch_saved_lease(None)
        # destroy() is also called directly by integration tests and host
        # applications; never leave a recovery lock handle open in that path.
        session = getattr(self, "_untitled_session", None)
        if session is not None:
            session.close()  # Keep any pending journal for recovery.
        super().destroy()

    def close_safely(self):
        if self._confirm_discard():
            if self._untitled_session is not None:
                self._untitled_session.close()
            self._switch_saved_lease(None)
            self.destroy()
    def new(self):
        if not self._confirm_discard():
            return
        document = {"nodes": [], "edges": []}
        self.history.reset(document)
        self.document = document
        self._switch_saved_lease(None)
        self.current_path = None
        self._saved_disk_digest = None
        self.selected = None
        self.selected_edge = None
        self.selected_nodes.clear()
        self.link_start = None
        self.saved_snapshot = self._snapshot()
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
        return node_at(project_editable(self.document)["nodes"], *self.viewport.world(x, y),
                       group_border_tolerance=6 / self.viewport.zoom)
    def edge_at(self, x, y):
        editable = project_editable(self.document)
        return edge_at(editable["nodes"], editable["edges"], *self.viewport.world(x, y), tolerance=9/self.viewport.zoom)
    def click(self, event):
        node = self.node_at(event.x, event.y)
        edge = (None if node is not None and node.get("shape") != "visio-group"
                else self.edge_at(event.x, event.y))
        node, edge = resolve_hit(node, edge)
        self._marquee_previous = set(self.selected_nodes)
        if self.link_start is not None and node is not None:
            if node["id"] != self.link_start:
                try:
                    self.document = connect_equipment(self.document, self.link_start, node["id"])
                    self._record_change()
                    self.status.set("Liaison créée entre les deux équipements")
                except ValueError as exc:
                    self.status.set(str(exc))
            else:
                self.status.set("Liaison annulée : choisissez deux équipements différents")
            self.link_start = None
        if node is None and (event.state & 0x0001):
            # Preserve existing selection until additive marquee completes.
            self.selected = None
        else:
            self.selected_nodes, self.selected = select_node(
                self.selected_nodes, node["id"] if node else None,
                ctrl=bool(event.state & 0x0004),
            )
        self.selected_edge = (edge or {}).get("id")
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
        editable_ids = {n["id"] for n in project_editable(self.document)["nodes"]}
        expanded = group_members(self.document["nodes"], self.selected_nodes)
        # A locked or hidden descendant must never be moved through its parent.
        if not expanded.issubset(editable_ids):
            self.status.set("Déplacement refusé : un membre du groupe est verrouillé ou masqué")
            return
        changed = move_group(self.document["nodes"], expanded, dx, dy, 20 if self.snap_enabled else None)
        if changed:
            self._drag_anchor = (x, y) if not self.snap_enabled else (old_x + snap(dx), old_y + snap(dy))
            self.draw()
    def begin_link(self):
        editable_ids = {n["id"] for n in project_editable(self.document)["nodes"]}
        if self.selected not in editable_ids:
            messagebox.showinfo("Connexion", "Sélectionnez d'abord un équipement")
            return
        self.link_start = self.selected
        self.status.set("Cliquez sur le second équipement pour créer la connexion")
    def edit_properties(self):
        node = next((n for n in self.document["nodes"] if n["id"] == self.selected), None)
        editable_ids = {n["id"] for n in project_editable(self.document)["nodes"]}
        if node is None or node["id"] not in editable_ids:
            messagebox.showinfo("Propriétés", "Sélectionnez un équipement")
            return
        if node.get("shape") == "visio-group":
            self.resize_selected_group()
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
        from .node_geometry import node_dimensions
        current_width, current_height = node_dimensions(node)
        width_var = tk.StringVar(value=f"{current_width:g}")
        height_var = tk.StringVar(value=f"{current_height:g}")
        dimension_row = shape_row + 1
        tk.Label(dialog, text="Dimensions (px)", anchor="w").grid(row=dimension_row, column=0, padx=12, pady=5, sticky="w")
        dimensions = tk.Frame(dialog)
        dimensions.grid(row=dimension_row, column=1, padx=12, pady=5, sticky="w")
        tk.Label(dimensions, text="L :").pack(side="left")
        tk.Entry(dimensions, textvariable=width_var, width=9).pack(side="left", padx=(0, 10))
        tk.Label(dimensions, text="H :").pack(side="left")
        tk.Entry(dimensions, textvariable=height_var, width=9).pack(side="left")
        def apply():
            try:
                raw = {key: (value.get("1.0", "end-1c") if key == "notes" else value.get()) for key, value in fields.items()}
                updated_document = update_equipment(self.document, node["id"], raw, shape.get(),
                                                    width=width_var.get(), height=height_var.get())
            except ValueError as exc:
                messagebox.showerror("Propriétés invalides", str(exc), parent=dialog)
                return
            self.document = updated_document
            self._record_change()
            self.draw()
            dialog.destroy()
        tk.Button(dialog, text="Enregistrer", command=apply).grid(row=shape_row+2, column=1, pady=12, sticky="e")
        dialog.bind("<Control-Return>", lambda event: apply())
        dialog.bind("<Escape>", lambda event: dialog.destroy())
        dialog.wait_window()
    def toggle_selected_edge_routing(self):
        editable = project_editable(self.document)
        edge = next((item for item in editable["edges"] if item["id"] == self.selected_edge), None)
        if edge is None:
            messagebox.showinfo("Routage", "Sélectionnez une liaison modifiable")
            return
        mode = "straight" if edge.get("routing") == "orthogonal" else "orthogonal"
        try:
            updated = set_edge_routing(self.document, edge["id"], mode)
        except (RoutingError, ValueError) as exc:
            messagebox.showerror("Routage impossible", str(exc), parent=self)
            return
        self.document = updated
        self._record_change()
        self.status.set("Routage " + ("orthogonal" if mode == "orthogonal" else "droit"))
        self.draw()

    def add_parallel_link(self):
        """Create a second physical path without inventing SAN port identities.

        The selected connection supplies endpoints; the operator must provide
        actual source/target ports. The normal undo/redo history records it.
        """
        edge = next((item for item in self.document['edges']
                     if item['id'] == self.selected_edge), None)
        editable_ids = {item['id'] for item in project_editable(self.document)['edges']}
        if edge is None or edge['id'] not in editable_ids:
            messagebox.showinfo('Chemins SAN', 'Sélectionnez une liaison modifiable', parent=self)
            return
        dialog = tk.Toplevel(self)
        dialog.title('Ajouter un chemin SAN physique')
        dialog.transient(self)
        dialog.grab_set()
        tk.Label(dialog, text='Indiquez les ports physiques du nouveau chemin. '
                 'Le chemin existant doit également avoir des ports distincts.',
                 wraplength=440, justify='left').grid(row=0, column=0, columnspan=2,
                                                      padx=12, pady=10, sticky='w')
        fields = {}
        for row, (key, label) in enumerate((('protocol', 'Protocole'),
                                           ('source_port', 'Port source'),
                                           ('target_port', 'Port cible'),
                                           ('fabric', 'Fabric'),
                                           ('speed_gbps', 'Débit Gbit/s')), 1):
            tk.Label(dialog, text=label).grid(row=row, column=0, padx=12, pady=5, sticky='w')
            default = edge.get('protocol', 'FC') if key == 'protocol' else ''
            value = tk.StringVar(value=default)
            if key == 'protocol':
                tk.OptionMenu(dialog, value, *PROTOCOLS).grid(row=row, column=1, padx=12, pady=5)
            else:
                tk.Entry(dialog, textvariable=value, width=36).grid(row=row, column=1,
                                                                     padx=12, pady=5)
            fields[key] = value

        def apply():
            metadata = {key: value.get() for key, value in fields.items()}
            if not metadata['source_port'].strip() or not metadata['target_port'].strip():
                messagebox.showerror('Chemin SAN', 'Deux ports physiques sont obligatoires', parent=dialog)
                return
            try:
                new_document = connect_equipment(self.document, edge['from'], edge['to'],
                                                 link=metadata, layer=edge.get('layer'))
            except ValueError as exc:
                messagebox.showerror('Chemin SAN', str(exc), parent=dialog)
                return
            self.document = new_document
            self.selected_edge = self.document['edges'][-1]['id']
            self.selected = None
            self.selected_nodes.clear()
            self._record_change()
            self.status.set('Chemin SAN parallèle créé ; vérifiez le routage et les ports')
            self.draw()
            dialog.destroy()

        tk.Button(dialog, text='Créer le chemin', command=apply).grid(row=6, column=1,
                                                                     pady=12, sticky='e')
        dialog.bind('<Escape>', lambda event: dialog.destroy())
        dialog.wait_window()

    def edit_selected_link(self):
        if not self.document["edges"]:
            messagebox.showinfo("Liaisons", "Créez d'abord une connexion")
            return
        edge = next((e for e in self.document["edges"] if e["id"] == self.selected_edge), None)
        editable_edges = {e["id"] for e in project_editable(self.document)["edges"]}
        if edge is None or edge["id"] not in editable_edges:
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
    def group_selected(self):
        editable = {n["id"] for n in project_editable(self.document)["nodes"]}
        ids = set(self.selected_nodes) & editable
        if ids != set(self.selected_nodes):
            self.status.set("Groupement refusé : sélection verrouillée ou masquée")
            return
        try:
            self.document, ident = group_selection(self.document, ids)
        except ValueError as exc:
            self.status.set(str(exc))
            return
        self.selected_nodes, self.selected = {ident}, ident
        self._record_change()
        self.draw()

    def ungroup_selected(self):
        ids = set(self.selected_nodes)
        if self.selected:
            ids.add(self.selected)
        nodes = {n["id"]: n for n in self.document["nodes"]}
        editable = {n["id"] for n in project_editable(self.document)["nodes"]}
        if not ids or not ids.issubset(editable):
            self.status.set("Dissociation refusée : sélection absente ou verrouillée")
            return
        if not group_members(self.document["nodes"], ids).issubset(editable):
            self.status.set("Dissociation refusée : membre verrouillé ou masqué")
            return
        try:
            self.document = ungroup_selection(self.document, ids)
        except ValueError as exc:
            self.status.set(str(exc))
            return
        self.selected_nodes.clear()
        self.selected = None
        self._record_change()
        self.draw()

    def resize_selected_group(self):
        ident = self.selected
        nodes = {n["id"]: n for n in self.document["nodes"]}
        node = nodes.get(ident)
        if node is None or node.get("shape") != "visio-group":
            self.status.set("Sélectionnez un groupe à redimensionner")
            return
        editable = {n["id"] for n in project_editable(self.document)["nodes"]}
        if not group_members(self.document["nodes"], {ident}).issubset(editable):
            self.status.set("Redimensionnement refusé : membre verrouillé ou masqué")
            return
        from .node_geometry import node_dimensions
        width, height = node_dimensions(node)
        new_width = simpledialog.askfloat("Redimensionner le groupe", "Largeur en pixels", initialvalue=width, minvalue=4, maxvalue=20000, parent=self)
        if new_width is None:
            return
        new_height = simpledialog.askfloat("Redimensionner le groupe", "Hauteur en pixels", initialvalue=height, minvalue=4, maxvalue=20000, parent=self)
        if new_height is None:
            return
        try:
            self.document = resize_group(self.document, ident, new_width, new_height)
        except ValueError as exc:
            self.status.set(str(exc))
            return
        self._record_change()
        self.draw()

    def delete_selected(self):
        ids = set(self.selected_nodes)
        if self.selected:
            ids.add(self.selected)
        editable = project_editable(self.document)
        ids.intersection_update({n["id"] for n in editable["nodes"]})
        selected_edge = self.selected_edge if self.selected_edge in {e["id"] for e in editable["edges"]} else None
        if not group_members(self.document["nodes"], ids).issubset({n["id"] for n in editable["nodes"]}):
            self.status.set("Suppression refusée : le groupe contient un membre verrouillé ou masqué")
            return
        if not ids and not selected_edge:
            return
        self.document = remove_selection(self.document, ids, selected_edge)
        self.selected = None
        self.selected_edge = None
        self.selected_nodes.clear()
        self.link_start = None
        self._record_change()
        self.status.set("Sélection supprimée ; liaison en attente annulée")
        self.draw()
    def draw(self):
        self._canvas_renderer.draw(project_visible(self.document), self.selected, self.selected_edge, self.viewport, grid=self.grid_enabled, selected_nodes=self.selected_nodes)
        self.canvas.delete("ov:marquee")
        if self._marquee_start is not None and self._marquee_end is not None:
            x0, y0 = self.viewport.screen(*self._marquee_start)
            x1, y1 = self.viewport.screen(*self._marquee_end)
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="#2563eb", dash=(5, 3), width=2, tags=("ov:marquee",))
        self._refresh_document_status()
    def restore_backup(self):
        """Load the validated previous version without silently overwriting the file."""
        if not self.current_path:
            messagebox.showinfo("Récupération", "Ouvrez d'abord un document enregistré.")
            return
        backup = backup_path(self.current_path)
        if not backup.is_file():
            messagebox.showinfo("Récupération", "Aucune sauvegarde précédente disponible.")
            return
        try:
            recovered, inspected = inspect_previous(self.current_path)
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror("Sauvegarde invalide", str(exc))
            return
        if not messagebox.askyesno(
            "Restaurer la version précédente",
            "Charger la sauvegarde précédente dans l'éditeur ? "
            "Les changements actuels seront remplacés. "
            "La sauvegarde ne sera pas écrasée.",
            parent=self,
        ):
            return
        if not self._confirm_discard():
            return
        # Preserve the recovered document as an undoable edit, even when it
        # matches the current history snapshot after the discard prompt.
        # The discard prompt may have saved the current file and rotated .bak.
        # Refuse restoration if the backup changed after user inspection.
        # Ask the user to restart restoration to inspect the new backup.
        try:
            recovered = restore_inspected(self.current_path, inspected)
        except (ValueError, OSError, UnicodeError, RuntimeError) as exc:
            messagebox.showerror("Sauvegarde modifiée ou invalide", str(exc))
            return
        self.document = replace_document(self.history, self.document, recovered)
        self.selected = self.selected_edge = None
        self.selected_nodes.clear()
        self.link_start = None
        self.status.set("Sauvegarde précédente chargée ; enregistrez pour la conserver")
        self.draw()

    def open(self, path=None):
        if path is None:
            path = filedialog.askopenfilename(filetypes=[("OpenVisio JSON", "*.ovjson *.json")])
        if not path:
            return
        # Reopening the current dirty file must not read a stale on-disk copy
        # before the save/discard decision changes that very same file.
        same_dirty = (self.current_path is not None
                      and Path(path).resolve()
                      == Path(self.current_path).resolve()
                      and self._snapshot() != self.saved_snapshot)
        if same_dirty and not self._confirm_discard():
            return
        try:
            document, disk_digest = open_document_with_revision(path)
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror("Ouverture impossible", str(exc))
            return
        recovered = False
        candidate = None
        try:
            entries, warnings = list_journals(path)
        except (OSError, ValueError) as exc:
            messagebox.showwarning("Récupération indisponible", str(exc), parent=self)
            entries, warnings = [], []
        if warnings:
            messagebox.showwarning("Journaux de récupération", "\n".join(warnings[:3]), parent=self)
        for entry in entries:
            if entry["document"] == document:
                continue
            answer = messagebox.askyesnocancel(
                "Version récupérable",
                "Une version non enregistrée de ce diagramme existe (" +
                ("ancien journal" if entry["session"] is None else "session distincte") +
                ").\nOui : récupérer en mémoire ; Non : supprimer uniquement ce journal ; "
                "Annuler : conserver et interrompre l'ouverture.", parent=self)
            if answer is None:
                return
            if answer:
                candidate = entry["document"]
                recovered = True
                break
            try:
                discard_journal(path, session_id=entry["session"])
            except OSError as exc:
                messagebox.showerror("Récupération", str(exc), parent=self)
                return
        if not same_dirty and not self._confirm_discard():
            return
        # The target may have changed while recovery prompts were displayed.
        # Never accept a stale model as the clean version of a newer file.
        try:
            if digest_file(path) != disk_digest:
                raise SaveConflict("Le document a changé pendant son ouverture ; recommencez")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Ouverture interrompue", str(exc), parent=self)
            return
        # Commit only after validation, journal inspection and user confirmation.
        original = document
        if recovered:
            document = candidate
        try:
            self._switch_saved_lease(path)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Récupération indisponible", str(exc), parent=self)
            return
        self.history.reset(document)
        self.document = document
        self.current_path = path
        self._saved_disk_digest = disk_digest
        self.selected = None
        self.selected_edge = None
        self.selected_nodes.clear()
        self.link_start = None
        self.saved_snapshot = json.dumps(original, sort_keys=True, ensure_ascii=False) if recovered else self._snapshot()
        self.draw()
        if recovered:
            self.status.set("Version récupérée en mémoire — enregistrez pour la conserver")
        return True
    def store(self):
        if not self.current_path: return self.store_as()
        try:
            if self._saved_disk_digest is None:
                raise SaveConflict("Version disque inconnue : utilisez Enregistrer sous")
            published_digest, save_issues = save_with_diagnostics(
                save_document_with_revision, self.current_path, self.document,
                expected_sha256=self._saved_disk_digest)
            self._saved_disk_digest = published_digest
            self.saved_snapshot = self._snapshot()
            try:
                discard_journal(self.current_path, session_id=self._saved_journal_id, lease=self._saved_lease)
            except OSError as exc:
                self.status.set("Document enregistré ; nettoyage du journal impossible : " + str(exc))
                self._refresh_document_status()
                display_save_diagnostics(self, save_issues)
                return
            self.status.set("Enregistré : " + self.current_path)
            self._refresh_document_status()
            display_save_diagnostics(self, save_issues)
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
    def import_from_vsdx(self, path=None):
        if path is None:
            path = filedialog.askopenfilename(filetypes=[("Visio VSDX", "*.vsdx")])
        if not path:
            return
        try:
            try:
                document = import_vsdx(path)
            except VsdxExternalChangesError as exc:
                if not messagebox.askyesno(
                        "VSDX modifié dans un éditeur externe",
                        str(exc) + "\n\nImporter seulement les formes et liaisons reconnues ? "
                        "Les propriétés, styles et calques d'origine peuvent être perdus.",
                        parent=self):
                    return
                document = import_vsdx(path, changed_pages="flatten")
        except (ValueError, OSError, UnicodeError, KeyError, __import__("zipfile").BadZipFile) as exc:
            messagebox.showerror("Import VSDX impossible", str(exc))
            return
        if not self._confirm_discard():
            return
        self.history.reset(document)
        self.document = document
        # VSDX is an import source, never a native JSON save destination.
        self._switch_saved_lease(None)
        self.current_path = None
        self._saved_disk_digest = None
        self.selected = self.selected_edge = None
        self.selected_nodes.clear()
        self.link_start = None
        self.saved_snapshot = "__import_vsdx_non_enregistre__"
        metadata = document.get("metadata", {})
        if metadata.get("import_mode") == "flattened-pages":
            count = metadata.get("page_count", 1)
            self.status.set(f"{count} page(s) VSDX importée(s) en calques — fidélité partielle ; enregistrez en .ovjson")
            warnings = metadata.get("fidelity_warnings", [])
            details = "\n".join(str(item) for item in warnings) if isinstance(warnings, list) else ""
            messagebox.showwarning(
                "Import VSDX partiel",
                f"{count} page(s) importée(s) sous forme de calques. "
                "Les groupes, masters, styles, rotations et formules Visio "
                "ne sont pas fidèlement conservés. Vérifiez le diagramme "
                "avant de l'utiliser en production."
                + ("\n\nDétails de fidélité :\n" + details if details else ""),
                parent=self)
        else:
            self.status.set("VSDX OpenVisio importé ; enregistrez au format .ovjson")
        self.draw()
        return True

    def export_as_vsdx(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".vsdx", filetypes=[("Visio VSDX (expérimental)", "*.vsdx")])
        if not path:
            return
        destination = Path(path)
        if destination.exists() or destination.is_symlink():
            if not messagebox.askyesno(
                    "Remplacer le VSDX ?",
                    "Ce fichier existe déjà. Confirmer son remplacement ?",
                    parent=self):
                return
            try:
                expected = digest_file(destination)
            except OSError as exc:
                messagebox.showerror("Export VSDX impossible", str(exc), parent=self)
                return
            require_absent = False
        else:
            expected = None
            require_absent = True
        try:
            export_vsdx(path, self.document, expected_sha256=expected,
                        require_absent=require_absent)
            self.status.set("VSDX expérimental exporté : " + path)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Export VSDX impossible", str(exc), parent=self)

    def store_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".ovjson", filetypes=[("OpenVisio", "*.ovjson")])
        if not path:
            return
        destination = Path(path)
        same_path = (self.current_path is not None
                     and destination.resolve() == Path(self.current_path).resolve())
        if same_path and not destination.exists():
            messagebox.showerror("Enregistrement impossible",
                                 "Le fichier d'origine a disparu ; choisissez un autre nom.", parent=self)
            return
        if destination.exists():
            if not same_path and not messagebox.askyesno(
                    "Remplacer le document ?",
                    "Le fichier existe déjà. Confirmer son remplacement ?", parent=self):
                return
            try:
                expected = (self._saved_disk_digest if same_path
                            else digest_file(destination))
            except OSError as exc:
                messagebox.showerror("Enregistrement impossible", str(exc), parent=self)
                return
            require_absent = False
        else:
            expected = None
            require_absent = True
        try:
            published_digest, save_issues = save_with_diagnostics(
                save_document_with_revision, path, self.document,
                expected_sha256=expected, require_absent=require_absent)
        except (ValueError, OSError) as exc:
            messagebox.showerror("Enregistrement impossible", str(exc), parent=self)
            return
        previous_path = self.current_path
        previous_lease = self._saved_lease
        self.current_path = path
        self._saved_disk_digest = published_digest
        self.saved_snapshot = self._snapshot()
        try:
            self._switch_saved_lease(path)
        except (OSError, ValueError) as exc:
            # The save succeeded; report the missing recovery guarantee.
            self._switch_saved_lease(None)
            self.status.set("Enregistré ; récupération automatique indisponible : " + str(exc))
            self._refresh_document_status()
            display_save_diagnostics(self, save_issues)
            return
        try:
            self._discard_untitled()
            # Never remove another editor's recovery journal.
            if previous_path:
                discard_journal(previous_path, session_id=self._saved_journal_id,
                                lease=previous_lease)
        except (OSError, ValueError) as exc:
            self.status.set("Document enregistré ; nettoyage du journal impossible : " + str(exc))
            self._refresh_document_status()
            display_save_diagnostics(self, save_issues)
            return
        self.status.set("Enregistré : " + path)
        self._refresh_document_status()
        display_save_diagnostics(self, save_issues)

def main(argv=None):
    """Open Explorer-provided OVJSON/VSDX arguments in the actual editor.

    Functional headless smoke takes precedence over command-line arguments.
    """
    import sys
    from .release_smoke import run_smoke_from_environment
    if run_smoke_from_environment():
        return
    from .startup import parse_startup_target, write_startup_receipt
    arguments = sys.argv[1:] if argv is None else argv
    editor = Editor()
    try:
        target = parse_startup_target(arguments)
    except ValueError as exc:
        editor.after_idle(lambda reason=str(exc): messagebox.showerror(
            "Ouverture impossible", reason, parent=editor))
    else:
        if target is not None:
            def open_on_startup():
                opened = (editor.import_from_vsdx(str(target.path)) if target.kind == 'vsdx'
                          else editor.open(str(target.path)))
                try:
                    write_startup_receipt(target, bool(opened), editor.document)
                except (OSError, ValueError) as exc:
                    editor.status.set("Rapport de qualification indisponible : " + str(exc))
            editor.after_idle(open_on_startup)
    editor.mainloop()
