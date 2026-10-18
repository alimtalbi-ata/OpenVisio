"""Build versioned Word/PDF documentation, clearly marking unverified evidence."""
from pathlib import Path
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "documentation"
OUT.mkdir(parents=True, exist_ok=True)
sections = [
 ("OpenVisio v42.0 — Guide Windows", "Auteur : Abdelhalim Talbi. Édition native Python/Tkinter."),
 ("Périmètre fonctionnel", "Version initiale : bibliothèque de huit types d'équipements (serveur, baie, switch SAN, NAS, switch réseau, pare-feu, base de données, application) ; créer, déplacer, relier et supprimer des équipements ; ouvrir et enregistrer des documents JSON ; exporter les diagrammes au format SVG vectoriel. Parité avec v41.77 non atteinte."),
 ("Installation", "Exécuter OpenVisio-Setup-v42.0-x64.exe sur Windows x64. L'application et l'interpréteur Python sont intégrés à l'exécutable. Aucun code source ni environnement Python requis sur le PC cible."),
 ("Portable", "Copier OpenVisio-v42.0-Windows-x64-Portable.exe sur le PC Windows x64 et le lancer. Aucun Node.js, Java, WebView2 ou .NET requis. Les bibliothèques Windows système et l'environnement graphique Windows restent nécessaires."),
 ("Utilisation", "Menu Équipements : choisir une forme infrastructure ; F2 : modifier nom, hôte/FQDN, adresse IPv4/IPv6, constructeur et modèle de l'équipement sélectionné ; Édition > Propriétés de la liaison sélectionnée : protocole FC/iSCSI/Ethernet/NFS/SMB/NVMe, ports, fabric et débit ; cliquer sur une liaison pour la sélectionner, modifier ses propriétés ou la supprimer ; double-clic sur le canevas : serveur ; glisser : déplacement ; menu Édition : créer une liaison ; Ctrl+O : ouvrir ; Ctrl+S : enregistrer ; Ctrl+Z : annuler ; Ctrl+Y : rétablir ; Fichier > Exporter en SVG : exporter une image vectorielle ; Suppr : supprimer."),
 ("Modèles de diagrammes infrastructure", "Le menu Modèles propose SAN double fabric (deux hôtes, deux fabrics FC, baie de stockage), NAS et clients (Linux NFS, Windows SMB, réseau Ethernet), et Application trois tiers (web, application, base de données). Chaque modèle génère des identifiants uniques et reste modifiable. L’ouverture d’un modèle demande confirmation avant d’abandonner un diagramme non enregistré."),
 ("Copie et duplication des topologies", "Ctrl+C copie les équipements sélectionnés et les connexions internes au groupe ; Ctrl+V colle une copie avec nouveaux identifiants et décalage progressif ; Ctrl+D duplique immédiatement. Suppr supprime le groupe et les liaisons associées. Ces opérations sont annulables avec Ctrl+Z."),
 ("Sélection rapide et glissement multiple", "Ctrl+A sélectionne tous les équipements du diagramme ; Échap annule la sélection. Après une sélection multiple par Ctrl+clic, un glissement sur n’importe quel équipement du groupe déplace le groupe entier sans perdre la sélection."),
 ("Déplacement groupé et distribution", "Sélectionnez plusieurs équipements avec Ctrl+clic, puis déplacez-les ensemble en glissant l’un des équipements sélectionnés. Le déplacement conserve les distances relatives et peut être annulé en une seule action. Le menu Affichage permet de distribuer régulièrement au moins trois équipements horizontalement ou verticalement."),
 ("Grille et alignement", "Le menu Affichage permet de montrer ou masquer la grille, activer ou désactiver l’accrochage magnétique (pas de 20 unités), puis aligner horizontalement ou verticalement plusieurs équipements sélectionnés avec Ctrl+clic. Les alignements sont enregistrés dans l’historique d’annulation."),
 ("Navigation du diagramme", "La molette de la souris zoome autour du pointeur, le bouton central maintenu déplace la vue, et le menu Affichage propose Ajuster à la fenêtre, Zoom +, Zoom - et Zoom 100 %. Les positions des équipements restent dans les coordonnées du document, indépendantes du zoom."),
 ("Export SVG adaptatif", "Le document SVG calcule désormais automatiquement son viewBox à partir des positions des équipements, avec marges, même si les coordonnées sont négatives ou éloignées. Les dimensions fixes restent possibles par appel API, sans couper les objets."),
 ("Architecture", "Tkinter (interface) -> modèle Python validé -> JSON atomique. PyInstaller compile le programme en EXE portable. Inno Setup crée l'installateur."),
 ("Compilation", "Sur Windows x64 avec Python 3.12, lancer python/Build-Windows.cmd. Le script installe PyInstaller dans un venv, exécute les tests, produit les deux exécutables, calcule SHA256 et construit l'archive cumulative."),
 ("Sécurité des modifications", "Lors de Nouveau, Ouvrir ou Quitter, OpenVisio propose Enregistrer, Ignorer ou Annuler lorsque le document contient des changements non enregistrés. La sauvegarde JSON est atomique et la validation rejette les identifiants dupliqués et les coordonnées non finies."),
 ("Audit et évolutions", "Une revue d’architecture détaillée et la feuille de route priorisée V42.1 à V42.8 sont intégrées au ZIP cumulatif sous 05-Documentation/technique/AUDIT-ARCHITECTURE-ROADMAP-V42.md. Les priorités immédiates sont la protection des données, l’annulation/rétablissement, la modularisation de l’éditeur et les tests fonctionnels Windows."),
 ("Validation", "Les tests automatisés valident la sérialisation, les identifiants et les références. L'exécution sur un PC Windows propre et les captures réelles doivent être effectuées séparément. Aucune capture réelle n'est fournie par ce générateur."),
 ("Limites", "Moteur SAN, import/export Visio, bibliothèque de formes avancée, routage, historique d'édition transactionnel avancé et parité v41.77 restent à développer. Ce document ne constitue pas une preuve de qualification Windows."),
]
doc = Document()
for i, (title, body) in enumerate(sections):
    doc.add_heading(title, 0 if i == 0 else 1)
    doc.add_paragraph(body)
doc.save(OUT / "OpenVisio-v42.0-Guide-Windows.docx")
styles = getSampleStyleSheet()
story = []
for i, (title, body) in enumerate(sections):
    story.extend([Paragraph(escape(title), styles["Title"] if i == 0 else styles["Heading2"]), Spacer(1, 9), Paragraph(escape(body), styles["BodyText"]), Spacer(1, 12)])
SimpleDocTemplate(str(OUT / "OpenVisio-v42.0-Guide-Windows.pdf"), pagesize=A4).build(story)
print("Documentation Word et PDF générée :", OUT)
