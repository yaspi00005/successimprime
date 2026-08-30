#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Termine le correctif precedent (ajouter_annulation_commande.py) :
le controleur PHP a ete applique avec succes chez vous, mais
templates/commandes/show.html.twig a une structure differente de
celle du brouillon (pas de bouton "Supprimer" sur cette page reelle,
en plus d'une indentation differente).

Ce script utilise des expressions regulieres tolerantes a
l'indentation ET a cette difference de structure, en s'appuyant
uniquement sur des reperes confirmes presents dans votre fichier
reel : le bloc "Modifier" (peutModifierCommande) et le commentaire
"CONTRÔLE PRÉPRESSE" qui le suit.

Usage:
    python3 finir_annulation_commande.py /chemin/vers/successImprim
"""

import os
import re
import sys


def erreur_fatale(message):
    print("\n[ERREUR FATALE] " + message)
    sys.exit(1)


def verifier_racine(racine):
    print("=" * 70)
    print("DIAGNOSTIC DE L'EMPLACEMENT")
    print("=" * 70)
    print("Repertoire courant (pwd)      : " + os.getcwd())
    print("Racine passee en argument     : " + racine)
    print("Racine resolue (chemin absolu): " + os.path.realpath(racine))

    composer_json = os.path.join(racine, "composer.json")
    if not os.path.isfile(composer_json):
        erreur_fatale(
            "Aucun 'composer.json' trouve dans " + os.path.realpath(racine) + "\n"
            "  => Relancez le script en pointant vers la racine du projet."
        )
    print("[OK] composer.json trouve : c'est bien la racine du projet.")
    print()


def appliquer_regex_verifie(racine, chemin_relatif, marqueur, remplacements):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if marqueur in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + marqueur + "' (deja applique).")
        return True

    contenu_original = contenu
    total = 0

    for motif, remplacement, description in remplacements:
        contenu, nb = motif.subn(remplacement, contenu, count=1)
        if nb == 0:
            print("[ECHEC] " + chemin_relatif + " : '" + description + "' introuvable -> abandon (rien ecrit).")
            return False
        total += nb
        print("  " + description + " : " + str(nb) + " remplacement(s)")

    if contenu == contenu_original:
        print("[ECHEC] " + chemin_relatif + " : aucun changement applique -> abandon.")
        return False

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (" + str(total) + " remplacement(s) au total)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


def ajouter_a_la_fin_verifie(racine, chemin_relatif, marqueur, suffixe_attendu, texte_a_ajouter):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if marqueur in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + marqueur + "' (deja applique).")
        return True

    contenu_sans_fin = contenu.rstrip("\n")

    if not contenu_sans_fin.endswith(suffixe_attendu.rstrip("\n")):
        print("[ECHEC] " + chemin_relatif + " : le fichier ne se termine pas comme attendu -> abandon (rien ecrit).")
        print("  Fin attendue : " + repr(suffixe_attendu[-80:]))
        print("  Fin reelle   : " + repr(contenu[-80:]))
        return False

    contenu_nouveau = contenu.rstrip("\n") + "\n" + texte_a_ajouter

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_nouveau)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_nouveau:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (texte ajoute en fin de fichier)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


# ============================================================
# 1) Condition du IF "Modifier" : ajoute "and commande.statutTravaux != 'annulee'"
# ============================================================

MOTIF_IF_MODIFIER = re.compile(
    r"(peutModifierCommande[ \t]*\n)"
    r"([ \t]*)(and\s*\([ \t]*\n[ \t]*not\s+commandeVerrouilleeProduction[ \t]*\n"
    r"[ \t]*or\s+estAdmin[ \t]*\n[ \t]*\)[ \t]*\n[ \t]*%\})"
)


def _remplacement_if_modifier(m):
    prefix = m.group(1)
    indent = m.group(2)
    reste = m.group(3)

    return prefix + indent + "and commande.statutTravaux != 'annulee'\n" + indent + reste


# ============================================================
# 2) Condition du ELSEIF "verrouillee" : meme ajout
# ============================================================

MOTIF_ELSEIF_MODIFIER = re.compile(
    r"(\{%-?\s*elseif[ \t]*\n[ \t]*commandeVerrouilleeProduction[ \t]*\n)"
    r"([ \t]*)(and\s+not\s+estAdmin[ \t]*\n[ \t]*%\})"
)


def _remplacement_elseif_modifier(m):
    prefix = m.group(1)
    indent = m.group(2)
    reste = m.group(3)

    return prefix + indent + "and commande.statutTravaux != 'annulee'\n" + indent + reste


# ============================================================
# 3) Bouton "Annuler la commande" juste avant le commentaire
#    "CONTRÔLE PRÉPRESSE" qui suit la section Modifier.
# ============================================================

MOTIF_AVANT_PREPRESSE = re.compile(
    r"(\{%-?\s*endif\s*-?%\})([ \t]*\n+)([ \t]*)(\{#.*?CONTRÔLE\s+PRÉPRESSE)",
    re.DOTALL
)


def _remplacement_bouton_annuler(m):
    endif_modifier = m.group(1)
    interligne = m.group(2)
    indent = m.group(3)
    debut_commentaire_suivant = m.group(4)

    unite = "\t" if ("\t" in indent or indent == "") else "    "
    i1 = indent + unite
    i2 = i1 + unite

    bloc_annuler = (
        indent + "{% if\n"
        + i1 + "peutModifierCommande\n"
        + i1 + "and commande.statutTravaux != 'annulee'\n"
        + i1 + "and (\n"
        + i2 + "not commandeVerrouilleeProduction\n"
        + i2 + "or estAdmin\n"
        + i1 + ")\n"
        + indent + "%}\n\n"
        + i1 + "<form method=\"post\" action=\"{{ path( 'app_commandes_annuler', { id: commande.id } ) }}\" "
        + "class=\"js-confirm-form d-inline\" data-message=\"Annuler la commande {{ commande.numero }} ? "
        + "Cette action est irréversible.\">\n\n"
        + i2 + "<input type=\"hidden\" name=\"_token\" value=\"{{ csrf_token( 'annuler-commande-' ~ commande.id ) }}\">\n\n"
        + i2 + "<button type=\"submit\" class=\"btn btn-sm btn-outline-danger mr-2 mb-2\">\n"
        + i2 + "\t<i class=\"fe fe-x-circle mr-1\"></i>\n"
        + i2 + "\tAnnuler la commande\n"
        + i2 + "</button>\n\n"
        + i1 + "</form>\n\n"
        + indent + "{% endif %}\n"
    )

    return endif_modifier + interligne + bloc_annuler + interligne + indent + debut_commentaire_suivant


# ============================================================
# 4) JS manquant pour que les confirmations (js-confirm-form)
#    fonctionnent vraiment sur cette page.
# ============================================================

TWIG_BLOC_JS_NOUVEAU = """

{% block javascripts %}

\t{{ parent() }}

\t<script>
\t\tdocument.addEventListener('DOMContentLoaded', function () {

\t\t\tconst formulaires = document.querySelectorAll('.js-confirm-form');

\t\t\tformulaires.forEach(function (formulaire) {

\t\t\t\tformulaire.addEventListener('submit', function (event) {

\t\t\t\t\tconst message = formulaire.dataset.message || 'Voulez-vous continuer ?';

\t\t\t\t\tif (!window.confirm(message)) {
\t\t\t\t\t\tevent.preventDefault();
\t\t\t\t\t}

\t\t\t\t});

\t\t\t});

\t\t});
\t</script>

{% endblock %}
"""

TWIG_MARQUEUR = "app_commandes_annuler"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    print("-" * 70)
    print("templates/commandes/show.html.twig")
    print("-" * 70)

    resultat = appliquer_regex_verifie(
        racine,
        "templates/commandes/show.html.twig",
        TWIG_MARQUEUR,
        [
            (MOTIF_IF_MODIFIER, _remplacement_if_modifier, "Condition IF Modifier (+ commande non annulee)"),
            (MOTIF_ELSEIF_MODIFIER, _remplacement_elseif_modifier, "Condition ELSEIF verrouillage (+ commande non annulee)"),
            (MOTIF_AVANT_PREPRESSE, _remplacement_bouton_annuler, "Bouton Annuler la commande"),
        ]
    )

    if resultat:
        resultat = ajouter_a_la_fin_verifie(
            racine,
            "templates/commandes/show.html.twig",
            "querySelectorAll('.js-confirm-form')",
            "</style>\n\n{% endblock %}",
            TWIG_BLOC_JS_NOUVEAU
        )

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if resultat:
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Sur la fiche d'une commande, un bouton 'Annuler la commande'")
        print("apparait juste apres le bouton Modifier, avec les memes regles")
        print("de verrouillage (tout le monde tant que la production n'a pas")
        print("commence, admin seulement ensuite).")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
