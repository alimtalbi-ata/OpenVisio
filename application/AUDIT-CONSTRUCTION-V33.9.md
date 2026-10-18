# Audit v33.9

Anomalie critique corrigée : dans le script v33.8, la compilation et la vérification finale pointaient encore vers `OpenVisio-Setup-v33.7-x64.exe` alors que la taille était contrôlée sur v33.8. Cela provoquait un faux échec ou un risque de validation d'un ancien artefact.

Mesures : synchronisation du nom v33.9 dans suppression, présence, taille, affichage et empreinte SHA-256 ; nettoyage du dossier de publication pour éviter les binaires périmés ; contrôles sur la création des dossiers ; tests de non-régression.

Restant : compiler et installer sur une VM Windows propre, vérifier le code WinForms/WebView2, les associations et les exports.
