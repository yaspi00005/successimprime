"""
Reporte automatiquement le nom du produit/article choisi dans le
champ "Désignation" de la ligne, aussi bien en commande qu'en devis.

Avant ce script, seul le choix d'un ARTICLE en stock remplissait la
désignation automatiquement. Le choix d'un PRODUIT du catalogue
(mode automatique via une configuration, ou mode manuel) laissait
la désignation vide côté client jusqu'à l'enregistrement.

Modifie :
- templates/commandes/_form.html.twig (2 points : configuration
  automatique + options manuelles/mode manuel)
- templates/devis/_form.html.twig (1 point : configuration)

A executer a la racine du dépôt : python3 report_designation_produit.py
"""

import sys


def appliquer(path, old, new, label):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if new in content:
        print(f"[SKIP] {label} : déjà présent dans {path}")
        return

    count = content.count(old)
    if count != 1:
        print(f"[ERREUR] {label} : {count} occurrence(s) trouvée(s) dans {path} (1 attendue)")
        sys.exit(1)

    content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] {label} appliqué à {path}")


TPL_COMMANDE = "templates/commandes/_form.html.twig"
TPL_DEVIS = "templates/devis/_form.html.twig"

appliquer(
    TPL_COMMANDE,
    """definirValeur(detail, 'prixUnitaire', infosProduit.prixBase || 0);

definirValeur(detail, 'remise', clientEstB2B() ? Math.round((infosProduit.remiseB2B || 0) * 100) / 100 : 0);

definirValeur(detail, 'modeCalcul', infosProduit.modeCalcul || 'unite');""",
    """definirValeur(detail, 'designation', infosProduit.nom || '');

definirValeur(detail, 'prixUnitaire', infosProduit.prixBase || 0);

definirValeur(detail, 'remise', clientEstB2B() ? Math.round((infosProduit.remiseB2B || 0) * 100) / 100 : 0);

definirValeur(detail, 'modeCalcul', infosProduit.modeCalcul || 'unite');""",
    "Désignation auto (mode manuel / options manuelles)",
)

appliquer(
    TPL_COMMANDE,
    """definirValeur(detail, 'typeImpression', config.typeImpression);

definirValeur(detail, 'support', config.support);

definirValeur(detail, 'format', config.format);

definirValeur(detail, 'prixUnitaire', config.prixBase || 0);""",
    """definirValeur(detail, 'designation', config.designation || '');

definirValeur(detail, 'typeImpression', config.typeImpression);

definirValeur(detail, 'support', config.support);

definirValeur(detail, 'format', config.format);

definirValeur(detail, 'prixUnitaire', config.prixBase || 0);""",
    "Désignation auto (mode automatique / configuration)",
)

appliquer(
    TPL_DEVIS,
    """definirValeurChamp(detail, 'typeImpression', configuration.typeImpression, false);

definirValeurChamp(detail, 'support', configuration.support, false);

definirValeurChamp(detail, 'format', configuration.format, false);""",
    """definirValeurChamp(detail, 'designation', configuration.designation || '', false);

definirValeurChamp(detail, 'typeImpression', configuration.typeImpression, false);

definirValeurChamp(detail, 'support', configuration.support, false);

definirValeurChamp(detail, 'format', configuration.format, false);""",
    "Désignation auto (configuration)",
)

print("\nTerminé.")
