/** OpenVisio v39.7 — raccourcis des actions principales. Auteur : Abdelhalim Talbi. */
export function primaryActionForKey(event) {
  if (!(event.ctrlKey || event.metaKey) || event.altKey || event.shiftKey) return null;
  const key = String(event.key || "").toLowerCase();
  return ({s:"saveJsonBtn",o:"openJsonBtn",n:"newDiagram"})[key] || null;
}
export function isTextEditingTarget(target) {
  if (!target) return false;
  if (target.isContentEditable) return true;
  if (target.closest?.("[contenteditable]:not([contenteditable=false]), [role=textbox]")) return true;
  const tag = String(target.tagName || "").toLowerCase();
  if (tag === "textarea" || tag === "select") return true;
  if (tag === "input") {
    const type = String(target.type || "text").toLowerCase();
    return !["button", "checkbox", "radio", "submit", "reset", "file", "range", "color"].includes(type);
  }
  return false;
}
export function installPrimaryShortcuts(doc = document) {
  doc.addEventListener("keydown", event => {
    const id = primaryActionForKey(event);
    if (!id || event.defaultPrevented || event.repeat || event.isComposing) return;
    // Ne pas remplacer le diagramme pendant une saisie de texte.
    const editing = isTextEditingTarget(event.target);
    if (editing && id !== "saveJsonBtn") return;
    const target = event.target;
    if (target?.closest?.("dialog[open], [role=dialog][aria-modal=true]")) return;
    const button = doc.getElementById(id);
    if (!button || button.disabled) return;
    event.preventDefault();
    button.click();
  });
}
