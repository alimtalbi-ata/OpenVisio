/** OpenVisio v39.7 — accès clavier à la bibliothèque. Auteur : Abdelhalim Talbi. */
export function libraryShortcut(event) {
  if (event.defaultPrevented || event.altKey || event.metaKey || event.ctrlKey || event.shiftKey) return null;
  if (event.target?.closest?.('input,textarea,select,[contenteditable="true"],dialog[open]')) return null;
  return event.key === '/' ? 'focus' : null;
}
export function installLibraryKeyboard(doc = document) {
  doc.addEventListener('keydown', event => {
    if (libraryShortcut(event) !== 'focus') return;
    const field = doc.getElementById('shapeSearch');
    if (!field || field.disabled || field.hidden) return;
    event.preventDefault(); field.focus(); field.select?.();
  });
}
