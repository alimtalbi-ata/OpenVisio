# OpenVisio v33.4 — Guide utilisateur Windows
Auteur : Abdelhalim Talbi

## Panneaux ajustables
Sur une fenêtre de plus de 850 px, faites glisser le bord droit de Bibliothèque ou le bord gauche d'Inspecteur. Au clavier, focalisez la séparation et utilisez les flèches (Maj pour accélérer). « ↺ Panneaux » rétablit les largeurs par défaut. Les dimensions sont conservées localement, sauf lorsque le stockage est indisponible.

## Construire l’installateur Windows
Exécuter `Build-OpenVisio-Windows.cmd` sous Windows connecté à Internet. Le script installe un SDK .NET local, cherche/installe Inno Setup avec winget, télécharge WebView2, publie l'application et compile l'installateur. Ces opérations ne sont pas qualifiées dans cet environnement Linux. L'utilisateur final n'a pas besoin du SDK .NET car la publication est autonome ; le runtime WebView2 est embarqué par l'installateur.

## Limites
L'interface reste partiellement monolithique. La compilation .NET, l'installation Windows, les tests d'interface natifs et les captures réelles ne sont pas exécutés ici.
