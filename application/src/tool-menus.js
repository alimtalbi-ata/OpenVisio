// OpenVisio — menu interactions. Auteur : Abdelhalim Talbi.
// Native <details> keeps keyboard activation and focus semantics.
export function installToolMenus(root) {
  const menus = Array.from(root.querySelectorAll('details.tool-menu'));
  const close = (except = null) => {
    for (const menu of menus) if (menu !== except) menu.open = false;
  };
  const onToggle = event => {
    const menu = event.currentTarget;
    if (menu.open) close(menu);
  };
  const onPointer = event => {
    if (!menus.some(menu => menu.contains(event.target))) close();
  };
  const onKey = event => {
    const openMenu = menus.find(menu => menu.open && menu.contains(event.target));
    if (openMenu && ['ArrowDown','ArrowUp','Home','End'].includes(event.key)) {
      const controls = Array.from(openMenu.querySelectorAll('button:not(:disabled),input:not(:disabled),select:not(:disabled),a[href],summary')).filter(item => !item.hidden);
      if (!controls.length) return;
      const current = controls.indexOf(root.activeElement);
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? controls.length - 1 : event.key === 'ArrowDown' ? (current + 1) % controls.length : (current < 0 ? controls.length - 1 : (current - 1 + controls.length) % controls.length);
      controls[next].focus();
      event.preventDefault?.();
      return;
    }
    if (event.key !== 'Escape' || !menus.some(menu => menu.open)) return;
    const active = root.activeElement;
    const owner = menus.find(menu => menu.open && menu.contains(active));
    close();
    if (owner) owner.querySelector('summary')?.focus();
    event.stopImmediatePropagation?.();
    event.stopPropagation?.();
  };
  const onClick = event => {
    const target = event.target;
    if (!target?.closest?.('button')) return;
    const menu = menus.find(item => item.contains(target));
    if (menu) { close(menu); menu.querySelector('summary')?.focus(); }
  };
  for (const menu of menus) menu.addEventListener('toggle', onToggle);
  root.addEventListener('pointerdown', onPointer);
  root.addEventListener('keydown', onKey);
  root.addEventListener('click', onClick);
  return () => {
    for (const menu of menus) menu.removeEventListener('toggle', onToggle);
    root.removeEventListener('pointerdown', onPointer);
    root.removeEventListener('keydown', onKey);
    root.removeEventListener('click', onClick);
  };
}
