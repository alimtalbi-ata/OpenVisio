# Audit approfondi OpenVisio v33.0 — Abdelhalim Talbi

## Constat vérifié sur les sources v32.9
- `index.html` monolithique avec de nombreux panneaux de diagnostic SAN, des dialogues et des sections imbriquées : coût élevé de maintenance et de lisibilité.
- Trois liens d'espaces spécialisés en position fixe, concurrents du ruban principal.
- Boutons de navigation et actions de fichier mélangés dans le même bandeau.
- `Build-Windows-Installer.cmd` suppose .NET SDK et Inno Setup installés ; pas de bootstrap.
- Installateur v32.9 se contente d'avertir si WebView2 est absent.
- Les tests JS ne prouvent pas le fonctionnement de l'EXE Windows.

## Actions v33.0
- Regroupement des trois liens fixes en menu compact « Espaces spécialisés ».
- Repères visuels Fichier/édition et Analyse/export dans la barre d'actions.
- Feuille CSS additive pour éviter de casser les identifiants JS existants.
- Un point d'entrée `Build-OpenVisio-Windows.cmd` : téléchargement SDK .NET 8 local, installation Inno Setup via winget, téléchargement runtime WebView2 x64, compilation et empaquetage.
- Le setup embarque WebView2 et le lance silencieusement si absent, avant OpenVisio.

## Dette technique / limites
- Refactoriser `index.html` en composants testables ; ne pas masquer arbitrairement les panneaux fonctionnels.
- Auditer l'ensemble des liens et modules secondaires, la persistance, les imports, l'accessibilité clavier et les performances DOM.
- Contrôler la signature Authenticode et les hashes SHA256 des outils téléchargés avant distribution entreprise.
- Tester la compilation sur Windows x64, les privilèges UAC, la détection WebView2, l'installation hors ligne et la désinstallation.
- Le bootstrap exige Internet pour la première compilation ; le setup final embarque les prérequis.
