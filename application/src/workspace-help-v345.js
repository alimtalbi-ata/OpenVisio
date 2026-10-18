// OpenVisio v34.5 — aide contextuelle non destructive. Auteur : Abdelhalim Talbi.
const HELP_ID = 'openvisio-shortcuts-help';
const shortcuts = [
  ['F1', 'Afficher ou fermer cette aide'],
  ['Ctrl + K', 'Rechercher une commande'],
  ['Ctrl + Maj + P', 'Rechercher une commande'],
  ['Ctrl + I', 'Afficher les propriétés'],
  ['Ctrl + Maj + F', 'Basculer en mode canevas seul'],
  ['Ctrl + O', 'Ouvrir un document (application Windows)'],
  ['Ctrl + S', 'Enregistrer / exporter selon le contexte'],
  ['Échap', 'Fermer le panneau actif']
];
function ensureHelp() {
  let dialog = document.getElementById(HELP_ID);
  if (dialog) return dialog;
  dialog = document.createElement('dialog');
  dialog.id = HELP_ID;
  dialog.setAttribute('aria-label', 'Aide et raccourcis clavier');
  dialog.className = 'workspace-help-dialog';
  const heading = document.createElement('h2');
  heading.textContent = 'Aide et raccourcis';
  dialog.append(heading);
  const intro = document.createElement('p');
  intro.textContent = 'Les raccourcis peuvent dépendre du mode Windows ou navigateur.';
  dialog.append(intro);
  const list = document.createElement('dl');
  for (const [key, action] of shortcuts) {
    const dt = document.createElement('dt'); dt.textContent = key;
    const dd = document.createElement('dd'); dd.textContent = action;
    list.append(dt, dd);
  }
  dialog.append(list);
  const close = document.createElement('button');
  close.type = 'button'; close.textContent = 'Fermer';
  close.addEventListener('click', () => dialog.close());
  dialog.append(close);
  document.body.append(dialog);
  return dialog;
}
function toggleHelp() {
  const dialog = ensureHelp();
  if (dialog.open) dialog.close(); else dialog.showModal();
}
document.getElementById('workspaceHelpBtn')?.addEventListener('click', toggleHelp);
document.addEventListener('keydown', event => {
  if (event.key === 'F1' && !event.altKey && !event.ctrlKey && !event.metaKey) {
    event.preventDefault(); toggleHelp();
  }
});
