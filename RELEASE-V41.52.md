# OpenVisio v41.52 — qualification de démarrage Windows

Auteur : Abdelhalim Talbi

## Livré

- Script `application/windows/Test-Windows-Startup.ps1` : démarrage réel des exécutables Native et Portable sur Windows, vérification de l’en-tête MZ, contrôle de survie du processus, fermeture et rapport JSON même en cas d’échec.
- Trois tests Node.js contrôlent les garanties structurelles du script.

## Exécution sur Windows (après compilation)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File windows/Test-Windows-Startup.ps1 -Mode Native
powershell -NoProfile -ExecutionPolicy Bypass -File windows/Test-Windows-Startup.ps1 -Mode Portable
```

Les rapports sont écrits dans `application/dist/qualification/startup-native.json` et `startup-portable.json`.

**Limites** : le script ne prouve pas l’affichage du WebView2 ni l’interactivité de l’interface. Les exécutables n’ont pas été compilés ou lancés sous Windows dans cet environnement Linux. Le test Node.js valide le script, pas le démarrage natif.

## Documentation
Les guides Word/PDF v41.51 sont conservés, mais aucun guide v41.52 n’est revendiqué.
