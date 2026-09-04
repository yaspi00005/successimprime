#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le prix et le "Mode de calcul" qui ne se remplissent pas au
changement de produit sur un devis.

Cause : au changement de produit, le formulaire appelait toujours la
fonction du mode "manuel" (chargerOptionsManuelles), meme quand le
mode reel de la ligne est "automatique" (le mode par defaut, celui
utilise quand le selecteur de mode a ete cache). Dans ce cas, la
liste des configurations du produit (d'ou viennent le prix et le
mode de calcul) n'etait jamais chargee.

Ce script fait en sorte que le bon chargement soit declenche selon le
mode reel de la ligne, et remet en place le remplissage immediat de
la designation des le choix du produit.

Usage:
    python3 corriger_prix_modecalcul_devis.py /chemin/vers/successImprim
"""

import os
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


ANCIEN = """if (produit) {
const produitChange = function () {

console.log('Produit changé :', produit.value);

chargerOptionsManuelles(detail);
};"""

NOUVEAU = """if (produit) {
const produitChange = function () {

console.log('Produit changé :', produit.value);

const optionProduit = produit.options[produit.selectedIndex];

const nomProduit = optionProduit && produit.value ? optionProduit.textContent.trim() : '';

definirValeurChamp(detail, 'designation', nomProduit, false);

if (valeurModeConfiguration(detail) === 'automatique') {
chargerConfigurationsProduit(detail, produit.value);
} else {
chargerOptionsManuelles(detail);
}
};"""

MARQUEUR = "valeurModeConfiguration(detail) === 'automatique') {\nchargerConfigurationsProduit(detail, produit.value);"


def corriger_fichier(racine, chemin_relatif):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja le correctif (deja applique).")
        return True

    if ANCIEN not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -B2 -A20 \"const produitChange = function\" " + chemin_relatif)
        return False

    if contenu.count(ANCIEN) > 1:
        print("[ECHEC] " + chemin_relatif + " : bloc de reference trouve plusieurs fois -> abandon par prudence.")
        return False

    contenu_corrige = contenu.replace(ANCIEN, NOUVEAU, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu_corrige)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu_corrige:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "templates/devis/_form.html.twig"

    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    resultat = corriger_fichier(racine, chemin_relatif)
    print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if resultat:
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Sur un devis, en changeant le produit d'une ligne, le prix")
        print("et le mode de calcul doivent maintenant se remplir")
        print("correctement (via la configuration du produit).")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
