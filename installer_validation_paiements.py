#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute l'option "Valider" (et Rejeter / Annuler) pour les paiements,
notamment les chèques, sur la page Paiements.

Le mécanisme (statuts en_attente/valide/rejete/annule, PaiementService
avec transactions + verrouillage + création du mouvement de trésorerie)
existait déjà entièrement côté code -- il manquait uniquement les
routes du contrôleur et les boutons dans les pages, qui étaient encore
au stade de gabarit brut (jamais terminées visuellement).

Modifie 4 fichiers :
  1) src/Controller/PaiementsController.php  -> routes valider/rejeter/annuler
  2) templates/paiements/index.html.twig     -> page refaite (liste + bouton Valider rapide)
  3) templates/paiements/show.html.twig      -> page refaite (détail + actions Valider/Rejeter/Annuler)
  4) templates/paiements/_delete_form.html.twig -> bouton Supprimer en français, stylé

Usage:
    python3 installer_validation_paiements.py /chemin/vers/successImprim
"""

import os
import sys
import shutil
import subprocess


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


PHP_LINT_DISPONIBLE = shutil.which("php") is not None


def lint_php_si_possible(chemin_absolu):
    if not PHP_LINT_DISPONIBLE:
        return
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=10,
        )
        sortie = (resultat.stdout + resultat.stderr).strip()
        if resultat.returncode == 0:
            print("  php -l : OK")
        else:
            print("  [ATTENTION] php -l a signale un probleme :")
            print("  " + sortie.replace("\n", "\n  "))
    except Exception as exc:
        print("  (php -l ignore : " + repr(exc) + ")")


def appliquer_blocs_verifie(racine, chemin_relatif, marqueur, blocs):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu_original = f.read()

    if marqueur in contenu_original:
        print("[SKIP] " + chemin_relatif + " contient deja '" + marqueur + "' (deja applique).")
        return True

    contenu = contenu_original
    for idx, (ancien, nouveau) in enumerate(blocs, start=1):
        occurrences = contenu.count(ancien)
        if occurrences != 1:
            print("[ECHEC] " + chemin_relatif + " : bloc " + str(idx) + "/" + str(len(blocs)) +
                  " trouve " + str(occurrences) + " fois au lieu de 1 -> abandon (rien ecrit sur ce fichier).")
            print("  Extrait attendu (debut) : " + repr(ancien[:150]))
            return False
        contenu = contenu.replace(ancien, nouveau, 1)

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != contenu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (" + str(len(blocs)) + " bloc(s) applique(s))")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    if chemin_relatif.endswith(".php"):
        lint_php_si_possible(chemin_absolu)
    return True


def remplacer_fichier_entier_verifie(racine, chemin_relatif, marqueurs_prealables, nouveau_contenu):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu_actuel = f.read()

    if contenu_actuel == nouveau_contenu:
        print("[SKIP] " + chemin_relatif + " est deja a jour.")
        return True

    manquants = [m for m in marqueurs_prealables if m not in contenu_actuel]

    if manquants:
        print("[ECHEC] " + chemin_relatif + " : le fichier ne correspond pas a l'etat attendu -> abandon.")
        print("  Marqueur(s) manquant(s) :")
        for m in manquants:
            print("    - " + repr(m[:80]))
        return False

    with open(chemin_absolu, "w", encoding="utf-8", newline="") as f:
        f.write(nouveau_contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin_absolu, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    if relu != nouveau_contenu:
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (fichier remplace)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True




# ============================================================
# Contenu complet des templates (generes depuis le bac a sable)
# ============================================================

INDEX_NOUVEAU = '{% extends \'base.html.twig\' %}\n\n{% block title %}\n\tPaiements\n{% endblock %}\n\n{% block body %}\n\n\t<div class="side-app">\n\n\t\t<div class="page-header">\n\n\t\t\t<div>\n\n\t\t\t\t<h1 class="page-title">\n\t\t\t\t\tPaiements\n\t\t\t\t</h1>\n\n\t\t\t\t<ol class="breadcrumb">\n\n\t\t\t\t\t<li class="breadcrumb-item">\n\t\t\t\t\t\tTrésorerie\n\t\t\t\t\t</li>\n\n\t\t\t\t\t<li class="breadcrumb-item active">\n\t\t\t\t\t\tPaiements\n\t\t\t\t\t</li>\n\n\t\t\t\t</ol>\n\n\t\t\t</div>\n\n\t\t\t<div>\n\n\t\t\t\t<a href="{{ path(\'app_paiements_new\') }}" class="btn btn-primary">\n\t\t\t\t\t<i class="fa fa-plus mr-1"></i>\n\t\t\t\t\tNouveau paiement\n\t\t\t\t</a>\n\n\t\t\t</div>\n\n\t\t</div>\n\n\n\t\t{% include "alert.html.twig" %}\n\n\n\t\t<div class="card">\n\n\t\t\t<div class="card-header">\n\t\t\t\t<h3 class="card-title mb-0">\n\t\t\t\t\tListe des paiements\n\t\t\t\t</h3>\n\t\t\t</div>\n\n\t\t\t<div class="table-responsive">\n\n\t\t\t\t<table class="table table-bordered table-hover mb-0">\n\n\t\t\t\t\t<thead>\n\n\t\t\t\t\t\t<tr>\n\t\t\t\t\t\t\t<th>#</th>\n\t\t\t\t\t\t\t<th class="text-right">Montant</th>\n\t\t\t\t\t\t\t<th>Mode</th>\n\t\t\t\t\t\t\t<th>Compte</th>\n\t\t\t\t\t\t\t<th>Commande</th>\n\t\t\t\t\t\t\t<th>Date</th>\n\t\t\t\t\t\t\t<th class="text-center">Statut</th>\n\t\t\t\t\t\t\t<th class="text-center">Actions</th>\n\t\t\t\t\t\t</tr>\n\n\t\t\t\t\t</thead>\n\n\t\t\t\t\t<tbody>\n\n\t\t\t\t\t\t{% for paiement in paiements %}\n\n\t\t\t\t\t\t\t<tr>\n\n\t\t\t\t\t\t\t\t<td class="align-middle">\n\t\t\t\t\t\t\t\t\t{{ paiement.id }}\n\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t<td class="align-middle text-right">\n\t\t\t\t\t\t\t\t\t{{ paiement.montant|number_format(0, \',\', \' \') }} FCFA\n\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t<td class="align-middle">\n\t\t\t\t\t\t\t\t\t{{ paiement.modeLabel }}\n\t\t\t\t\t\t\t\t\t{% if paiement.estCheque and paiement.numeroCheque %}\n\t\t\t\t\t\t\t\t\t\t<div class="small text-muted">\n\t\t\t\t\t\t\t\t\t\t\tN° {{ paiement.numeroCheque }}\n\t\t\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t<td class="align-middle">\n\t\t\t\t\t\t\t\t\t{{ paiement.compteTresorerie ? paiement.compteTresorerie.nom : \'—\' }}\n\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t<td class="align-middle">\n\t\t\t\t\t\t\t\t\t{% if paiement.commande %}\n\t\t\t\t\t\t\t\t\t\t<a href="{{ path(\'app_commandes_show\', { id: paiement.commande.id }) }}">\n\t\t\t\t\t\t\t\t\t\t\t{{ paiement.commande.numero|default(\'#\' ~ paiement.commande.id) }}\n\t\t\t\t\t\t\t\t\t\t</a>\n\t\t\t\t\t\t\t\t\t{% else %}\n\t\t\t\t\t\t\t\t\t\t—\n\t\t\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t<td class="align-middle nowrap">\n\t\t\t\t\t\t\t\t\t{{ paiement.date ? paiement.date|date(\'d/m/Y H:i\') : \'—\' }}\n\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t<td class="align-middle text-center">\n\n\t\t\t\t\t\t\t\t\t{% if paiement.estEnAttente %}\n\t\t\t\t\t\t\t\t\t\t<span class="badge badge-warning">En attente</span>\n\t\t\t\t\t\t\t\t\t{% elseif paiement.estValide %}\n\t\t\t\t\t\t\t\t\t\t<span class="badge badge-success">Validé</span>\n\t\t\t\t\t\t\t\t\t{% elseif paiement.estRejete %}\n\t\t\t\t\t\t\t\t\t\t<span class="badge badge-danger">Rejeté</span>\n\t\t\t\t\t\t\t\t\t{% elseif paiement.estAnnule %}\n\t\t\t\t\t\t\t\t\t\t<span class="badge badge-secondary">Annulé</span>\n\t\t\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t\t<td class="align-middle text-center nowrap">\n\n\t\t\t\t\t\t\t\t\t<div class="btn-group">\n\n\t\t\t\t\t\t\t\t\t\t<a href="{{ path(\'app_paiements_show\', { id: paiement.id }) }}" class="btn btn-sm btn-primary-light" title="Voir le détail">\n\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-eye"></i>\n\t\t\t\t\t\t\t\t\t\t</a>\n\n\t\t\t\t\t\t\t\t\t\t{% if paiement.estEnAttente %}\n\n\t\t\t\t\t\t\t\t\t\t\t<form method="post" action="{{ path(\'app_paiements_valider\', { id: paiement.id }) }}" class="d-inline js-confirmer-validation" data-libelle="ce paiement de {{ paiement.montant|number_format(0, \',\', \' \') }} FCFA">\n\t\t\t\t\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token(\'paiement_valider\' ~ paiement.id) }}">\n\t\t\t\t\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-sm btn-success" title="Valider">\n\t\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-check"></i>\n\t\t\t\t\t\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t</td>\n\n\t\t\t\t\t\t\t</tr>\n\n\t\t\t\t\t\t{% else %}\n\n\t\t\t\t\t\t\t<tr>\n\t\t\t\t\t\t\t\t<td colspan="8" class="text-center text-muted py-5">\n\t\t\t\t\t\t\t\t\tAucun paiement enregistré.\n\t\t\t\t\t\t\t\t</td>\n\t\t\t\t\t\t\t</tr>\n\n\t\t\t\t\t\t{% endfor %}\n\n\t\t\t\t\t</tbody>\n\n\t\t\t\t</table>\n\n\t\t\t</div>\n\n\t\t</div>\n\n\t</div>\n\n\t<script>\n\t\tdocument.addEventListener(\'DOMContentLoaded\', function () {\n\ndocument.querySelectorAll(\'.js-confirmer-validation\').forEach(function (formulaire) {\n\nformulaire.addEventListener(\'submit\', function (event) {\n\nevent.preventDefault();\n\nconst libelle = formulaire.dataset.libelle || \'ce paiement\';\n\nif (typeof Swal === \'undefined\') {\nformulaire.submit();\nreturn;\n}\n\nSwal.fire({\nicon: \'question\',\ntitle: \'Valider ce paiement ?\',\nhtml: \'Confirmer la validation de <strong>\' + libelle + \'</strong> ?<br><br><small>Le compte de trésorerie sera crédité immédiatement.</small>\',\nshowCancelButton: true,\nconfirmButtonText: \'Oui, valider\',\ncancelButtonText: \'Annuler\',\nreverseButtons: true\n}).then(function (resultat) {\nif (resultat.isConfirmed) {\nformulaire.submit();\n}\n});\n\n});\n\n});\n\n});\n\t</script>\n\n{% endblock %}\n'

SHOW_NOUVEAU = '{% extends \'base.html.twig\' %}\n\n{% block title %}\n\tPaiement #{{ paiement.id }}\n{% endblock %}\n\n{% block body %}\n\n\t<div class="side-app">\n\n\t\t<div class="page-header">\n\n\t\t\t<div>\n\n\t\t\t\t<ol class="breadcrumb">\n\n\t\t\t\t\t<li class="breadcrumb-item">\n\t\t\t\t\t\t<a href="{{ path(\'app_paiements_index\') }}">\n\t\t\t\t\t\t\tPaiements\n\t\t\t\t\t\t</a>\n\t\t\t\t\t</li>\n\n\t\t\t\t\t<li class="breadcrumb-item active">\n\t\t\t\t\t\tPaiement #{{ paiement.id }}\n\t\t\t\t\t</li>\n\n\t\t\t\t</ol>\n\n\t\t\t</div>\n\n\t\t\t<div>\n\n\t\t\t\t<a href="{{ path(\'app_paiements_index\') }}" class="btn btn-primary-light">\n\t\t\t\t\t<i class="fa fa-arrow-left mr-1"></i>\n\t\t\t\t\tRetour à la liste\n\t\t\t\t</a>\n\n\t\t\t</div>\n\n\t\t</div>\n\n\n\t\t{% include "alert.html.twig" %}\n\n\n\t\t<div class="row">\n\n\t\t\t<div class="col-lg-8">\n\n\t\t\t\t<div class="card">\n\n\t\t\t\t\t<div class="card-header d-flex justify-content-between align-items-center flex-wrap">\n\n\t\t\t\t\t\t<h3 class="card-title mb-0">\n\t\t\t\t\t\t\tDétail du paiement\n\t\t\t\t\t\t</h3>\n\n\t\t\t\t\t\t<div>\n\n\t\t\t\t\t\t\t{% if paiement.estEnAttente %}\n\t\t\t\t\t\t\t\t<span class="badge badge-warning">En attente</span>\n\t\t\t\t\t\t\t{% elseif paiement.estValide %}\n\t\t\t\t\t\t\t\t<span class="badge badge-success">Validé</span>\n\t\t\t\t\t\t\t{% elseif paiement.estRejete %}\n\t\t\t\t\t\t\t\t<span class="badge badge-danger">Rejeté</span>\n\t\t\t\t\t\t\t{% elseif paiement.estAnnule %}\n\t\t\t\t\t\t\t\t<span class="badge badge-secondary">Annulé</span>\n\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t</div>\n\n\t\t\t\t\t</div>\n\n\t\t\t\t\t<div class="card-body">\n\n\t\t\t\t\t\t<div class="row">\n\n\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t<small class="text-muted d-block">Montant</small>\n\t\t\t\t\t\t\t\t<strong>{{ paiement.montant|number_format(0, \',\', \' \') }} FCFA</strong>\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t<small class="text-muted d-block">Mode de paiement</small>\n\t\t\t\t\t\t\t\t{{ paiement.modeLabel }}\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t<small class="text-muted d-block">Compte de trésorerie</small>\n\t\t\t\t\t\t\t\t{{ paiement.compteTresorerie ? paiement.compteTresorerie.nom : \'—\' }}\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t<small class="text-muted d-block">Commande</small>\n\t\t\t\t\t\t\t\t{% if paiement.commande %}\n\t\t\t\t\t\t\t\t\t<a href="{{ path(\'app_commandes_show\', { id: paiement.commande.id }) }}">\n\t\t\t\t\t\t\t\t\t\t{{ paiement.commande.numero|default(\'#\' ~ paiement.commande.id) }}\n\t\t\t\t\t\t\t\t\t</a>\n\t\t\t\t\t\t\t\t{% else %}\n\t\t\t\t\t\t\t\t\t—\n\t\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t<small class="text-muted d-block">Date</small>\n\t\t\t\t\t\t\t\t{{ paiement.date ? paiement.date|date(\'d/m/Y H:i\') : \'—\' }}\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t<small class="text-muted d-block">Référence</small>\n\t\t\t\t\t\t\t\t{{ paiement.reference|default(\'—\') }}\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t{% if paiement.estCheque %}\n\n\t\t\t\t\t\t\t\t<div class="col-12">\n\t\t\t\t\t\t\t\t\t<hr>\n\t\t\t\t\t\t\t\t\t<h5 class="mb-3">\n\t\t\t\t\t\t\t\t\t\t<i class="fa fa-money mr-1"></i>\n\t\t\t\t\t\t\t\t\t\tInformations du chèque\n\t\t\t\t\t\t\t\t\t</h5>\n\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t\t<small class="text-muted d-block">N° du chèque</small>\n\t\t\t\t\t\t\t\t\t{{ paiement.numeroCheque|default(\'—\') }}\n\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t\t<small class="text-muted d-block">Banque émettrice</small>\n\t\t\t\t\t\t\t\t\t{{ paiement.banqueEmettrice|default(\'—\') }}\n\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t\t<small class="text-muted d-block">Titulaire</small>\n\t\t\t\t\t\t\t\t\t{{ paiement.titulaireCheque|default(\'—\') }}\n\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t<div class="col-md-6 mb-3">\n\t\t\t\t\t\t\t\t\t<small class="text-muted d-block">Date d\'encaissement prévue</small>\n\t\t\t\t\t\t\t\t\t{{ paiement.dateEncaissementPrevue ? paiement.dateEncaissementPrevue|date(\'d/m/Y\') : \'—\' }}\n\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t\t{% if paiement.observation %}\n\t\t\t\t\t\t\t\t<div class="col-12 mb-3">\n\t\t\t\t\t\t\t\t\t<small class="text-muted d-block">Observation</small>\n\t\t\t\t\t\t\t\t\t{{ paiement.observation }}\n\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t\t{% if paiement.estRejete and paiement.motifRejet %}\n\t\t\t\t\t\t\t\t<div class="col-12">\n\t\t\t\t\t\t\t\t\t<div class="alert alert-danger mb-0">\n\t\t\t\t\t\t\t\t\t\t<strong>Motif du rejet :</strong>\n\t\t\t\t\t\t\t\t\t\t{{ paiement.motifRejet }}\n\t\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t\t{% if paiement.estAnnule and paiement.motifAnnulation %}\n\t\t\t\t\t\t\t\t<div class="col-12">\n\t\t\t\t\t\t\t\t\t<div class="alert alert-secondary mb-0">\n\t\t\t\t\t\t\t\t\t\t<strong>Motif de l\'annulation :</strong>\n\t\t\t\t\t\t\t\t\t\t{{ paiement.motifAnnulation }}\n\t\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t\t</div>\n\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t</div>\n\n\t\t\t\t\t</div>\n\n\t\t\t\t</div>\n\n\t\t\t</div>\n\n\n\t\t\t<div class="col-lg-4">\n\n\t\t\t\t<div class="card">\n\n\t\t\t\t\t<div class="card-header">\n\t\t\t\t\t\t<h3 class="card-title mb-0">\n\t\t\t\t\t\t\tActions\n\t\t\t\t\t\t</h3>\n\t\t\t\t\t</div>\n\n\t\t\t\t\t<div class="card-body">\n\n\t\t\t\t\t\t{% if paiement.estEnAttente %}\n\n\t\t\t\t\t\t\t<form method="post" action="{{ path(\'app_paiements_valider\', { id: paiement.id }) }}" class="mb-2 js-confirmer-validation" data-libelle="ce paiement de {{ paiement.montant|number_format(0, \',\', \' \') }} FCFA">\n\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token(\'paiement_valider\' ~ paiement.id) }}">\n\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-success btn-block">\n\t\t\t\t\t\t\t\t\t<i class="fa fa-check mr-1"></i>\n\t\t\t\t\t\t\t\t\tValider le paiement\n\t\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t\t<form method="post" action="{{ path(\'app_paiements_rejeter\', { id: paiement.id }) }}" class="mb-2 js-demander-motif" data-titre="Rejeter ce paiement" data-texte="Merci d\'indiquer le motif du rejet.">\n\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token(\'paiement_rejeter\' ~ paiement.id) }}">\n\t\t\t\t\t\t\t\t<input type="hidden" name="motif" value="">\n\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-danger-light btn-block">\n\t\t\t\t\t\t\t\t\t<i class="fa fa-times mr-1"></i>\n\t\t\t\t\t\t\t\t\tRejeter le paiement\n\t\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t\t<div class="small text-muted mt-2">\n\t\t\t\t\t\t\t\t<i class="fa fa-info-circle mr-1"></i>\n\t\t\t\t\t\t\t\tValider crédite immédiatement le compte de trésorerie choisi.\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t{% elseif paiement.estValide %}\n\n\t\t\t\t\t\t\t<form method="post" action="{{ path(\'app_paiements_annuler\', { id: paiement.id }) }}" class="mb-2 js-demander-motif" data-titre="Annuler ce paiement" data-texte="Merci d\'indiquer le motif de l\'annulation.">\n\t\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token(\'paiement_annuler\' ~ paiement.id) }}">\n\t\t\t\t\t\t\t\t<input type="hidden" name="motif" value="">\n\t\t\t\t\t\t\t\t<button type="submit" class="btn btn-danger btn-block">\n\t\t\t\t\t\t\t\t\t<i class="fa fa-undo mr-1"></i>\n\t\t\t\t\t\t\t\t\tAnnuler le paiement\n\t\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t\t</form>\n\n\t\t\t\t\t\t\t<div class="small text-muted mt-2">\n\t\t\t\t\t\t\t\t<i class="fa fa-info-circle mr-1"></i>\n\t\t\t\t\t\t\t\tAnnuler débite le compte de trésorerie du montant déjà crédité.\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t{% else %}\n\n\t\t\t\t\t\t\t<div class="text-muted small">\n\t\t\t\t\t\t\t\tAucune action possible sur un paiement\n\t\t\t\t\t\t\t\t{{ paiement.estRejete ? \'rejeté\' : \'annulé\' }}.\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t<hr>\n\n\t\t\t\t\t\t<a href="{{ path(\'app_paiements_edit\', { id: paiement.id }) }}" class="btn btn-light btn-block">\n\t\t\t\t\t\t\t<i class="fa fa-pencil mr-1"></i>\n\t\t\t\t\t\t\tModifier\n\t\t\t\t\t\t</a>\n\n\t\t\t\t\t\t{{ include(\'paiements/_delete_form.html.twig\') }}\n\n\t\t\t\t\t</div>\n\n\t\t\t\t</div>\n\n\t\t\t</div>\n\n\t\t</div>\n\n\t</div>\n\n\t<script>\n\t\tdocument.addEventListener(\'DOMContentLoaded\', function () {\n\ndocument.querySelectorAll(\'.js-confirmer-validation\').forEach(function (formulaire) {\n\nformulaire.addEventListener(\'submit\', function (event) {\n\nevent.preventDefault();\n\nconst libelle = formulaire.dataset.libelle || \'ce paiement\';\n\nif (typeof Swal === \'undefined\') {\nformulaire.submit();\nreturn;\n}\n\nSwal.fire({\nicon: \'question\',\ntitle: \'Valider ce paiement ?\',\nhtml: \'Confirmer la validation de <strong>\' + libelle + \'</strong> ?<br><br><small>Le compte de trésorerie sera crédité immédiatement.</small>\',\nshowCancelButton: true,\nconfirmButtonText: \'Oui, valider\',\ncancelButtonText: \'Annuler\',\nreverseButtons: true\n}).then(function (resultat) {\nif (resultat.isConfirmed) {\nformulaire.submit();\n}\n});\n\n});\n\n});\n\n\ndocument.querySelectorAll(\'.js-demander-motif\').forEach(function (formulaire) {\n\nformulaire.addEventListener(\'submit\', function (event) {\n\nevent.preventDefault();\n\nconst champMotif = formulaire.querySelector(\'input[name="motif"]\');\n\nconst titre = formulaire.dataset.titre || \'Confirmer\';\n\nconst texte = formulaire.dataset.texte || \'Merci d’indiquer un motif.\';\n\nif (typeof Swal === \'undefined\') {\n\nconst motif = window.prompt(texte);\n\nif (motif === null || motif.trim() === \'\') {\nreturn;\n}\n\nif (champMotif) {\nchampMotif.value = motif.trim();\n}\n\nformulaire.submit();\n\nreturn;\n}\n\nSwal.fire({\nicon: \'warning\',\ntitle: titre,\ntext: texte,\ninput: \'text\',\ninputPlaceholder: \'Motif...\',\nshowCancelButton: true,\nconfirmButtonText: \'Confirmer\',\ncancelButtonText: \'Annuler\',\nreverseButtons: true,\ninputValidator: function (valeur) {\nif (! valeur || ! valeur.trim()) {\nreturn \'Le motif est obligatoire.\';\n}\n}\n}).then(function (resultat) {\n\nif (resultat.isConfirmed) {\n\nif (champMotif) {\nchampMotif.value = resultat.value.trim();\n}\n\nformulaire.submit();\n}\n\n});\n\n});\n\n});\n\n});\n\t</script>\n\n{% endblock %}\n'

DELETE_FORM_NOUVEAU = '<form method="post" action="{{ path(\'app_paiements_delete\', {\'id\': paiement.id}) }}" class="mt-2" onsubmit="return confirm(\'Supprimer définitivement ce paiement ?\');">\n    <input type="hidden" name="_token" value="{{ csrf_token(\'delete\' ~ paiement.id) }}">\n    <button type="submit" class="btn btn-danger-light btn-block">\n        <i class="fa fa-trash mr-1"></i>\n        Supprimer\n    </button>\n</form>\n'

# ============================================================
# 1) src/Controller/PaiementsController.php
# ============================================================

CTRL_BLOC_1_ANCIEN = """use App\\Entity\\Paiements;
use App\\Form\\PaiementsType;
use App\\Repository\\PaiementsRepository;
use Doctrine\\ORM\\EntityManagerInterface;
use Symfony\\Bundle\\FrameworkBundle\\Controller\\AbstractController;
use Symfony\\Component\\HttpFoundation\\Request;
use Symfony\\Component\\HttpFoundation\\Response;
use Symfony\\Component\\Routing\\Attribute\\Route;"""

CTRL_BLOC_1_NOUVEAU = """use App\\Entity\\Paiements;
use App\\Entity\\User;
use App\\Form\\PaiementsType;
use App\\Repository\\PaiementsRepository;
use App\\Service\\PaiementService;
use Doctrine\\ORM\\EntityManagerInterface;
use Symfony\\Bundle\\FrameworkBundle\\Controller\\AbstractController;
use Symfony\\Component\\HttpFoundation\\Request;
use Symfony\\Component\\HttpFoundation\\Response;
use Symfony\\Component\\Routing\\Attribute\\Route;
use Symfony\\Component\\Security\\Http\\Attribute\\IsGranted;"""

CTRL_BLOC_2_ANCIEN = """    #[Route('/{id}', name: 'app_paiements_delete', methods: ['POST'])]
    public function delete(Request $request, Paiements $paiement, EntityManagerInterface $entityManager): Response
    {
        if ($this->isCsrfTokenValid('delete'.$paiement->getId(), $request->getPayload()->getString('_token'))) {
            $entityManager->remove($paiement);
            $entityManager->flush();
        }

        return $this->redirectToRoute('app_paiements_index', [], Response::HTTP_SEE_OTHER);
    }
}"""

CTRL_BLOC_2_NOUVEAU = """    #[Route('/{id}', name: 'app_paiements_delete', methods: ['POST'])]
    public function delete(Request $request, Paiements $paiement, EntityManagerInterface $entityManager): Response
    {
        if ($this->isCsrfTokenValid('delete'.$paiement->getId(), $request->getPayload()->getString('_token'))) {
            $entityManager->remove($paiement);
            $entityManager->flush();
        }

        return $this->redirectToRoute('app_paiements_index', [], Response::HTTP_SEE_OTHER);
    }

    #[Route('/{id}/valider', name: 'app_paiements_valider', methods: ['POST'])]
    #[IsGranted('ROLE_PAIEMENT_ENCAISSER')]
    public function valider(Request $request, Paiements $paiement, PaiementService $paiementService): Response
    {
        if ($this->isCsrfTokenValid('paiement_valider' . $paiement->getId(), $request->getPayload()->getString('_token'))) {
            try {
                $paiementService->valider($paiement, $this->utilisateurConnecte());

                $this->addFlash('success', 'Le paiement a été validé et le compte crédité.');
            } catch (\\Throwable $exception) {
                $this->addFlash('error', $exception->getMessage());
            }
        }

        return $this->redirectToRoute('app_paiements_show', ['id' => $paiement->getId()], Response::HTTP_SEE_OTHER);
    }

    #[Route('/{id}/rejeter', name: 'app_paiements_rejeter', methods: ['POST'])]
    #[IsGranted('ROLE_PAIEMENT_ENCAISSER')]
    public function rejeter(Request $request, Paiements $paiement, PaiementService $paiementService): Response
    {
        if ($this->isCsrfTokenValid('paiement_rejeter' . $paiement->getId(), $request->getPayload()->getString('_token'))) {
            try {
                $motif = trim((string) $request->getPayload()->getString('motif'));

                $paiementService->rejeter($paiement, $motif, $this->utilisateurConnecte());

                $this->addFlash('success', 'Le paiement a été rejeté.');
            } catch (\\Throwable $exception) {
                $this->addFlash('error', $exception->getMessage());
            }
        }

        return $this->redirectToRoute('app_paiements_show', ['id' => $paiement->getId()], Response::HTTP_SEE_OTHER);
    }

    #[Route('/{id}/annuler', name: 'app_paiements_annuler', methods: ['POST'])]
    #[IsGranted('ROLE_PAIEMENT_ENCAISSER')]
    public function annuler(Request $request, Paiements $paiement, PaiementService $paiementService): Response
    {
        if ($this->isCsrfTokenValid('paiement_annuler' . $paiement->getId(), $request->getPayload()->getString('_token'))) {
            try {
                $motif = trim((string) $request->getPayload()->getString('motif'));

                $paiementService->annuler($paiement, $motif, $this->utilisateurConnecte());

                $this->addFlash('success', 'Le paiement a été annulé et le compte débité.');
            } catch (\\Throwable $exception) {
                $this->addFlash('error', $exception->getMessage());
            }
        }

        return $this->redirectToRoute('app_paiements_show', ['id' => $paiement->getId()], Response::HTTP_SEE_OTHER);
    }

    private function utilisateurConnecte(): User
    {
        $utilisateur = $this->getUser();

        if (!$utilisateur instanceof User) {
            throw $this->createAccessDeniedException('Utilisateur non authentifié.');
        }

        return $utilisateur;
    }
}"""

CTRL_MARQUEUR = "app_paiements_valider"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    if not PHP_LINT_DISPONIBLE:
        print("(info : commande 'php' introuvable ici, le controle 'php -l' sera saute)")
        print()

    resultats = []

    print("-" * 70)
    print("1) src/Controller/PaiementsController.php")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "src/Controller/PaiementsController.php",
        CTRL_MARQUEUR,
        [
            (CTRL_BLOC_1_ANCIEN, CTRL_BLOC_1_NOUVEAU),
            (CTRL_BLOC_2_ANCIEN, CTRL_BLOC_2_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("2) templates/paiements/index.html.twig")
    print("-" * 70)
    resultats.append(remplacer_fichier_entier_verifie(
        racine,
        "templates/paiements/index.html.twig",
        [
            "{% block title %}Paiements index{% endblock %}",
            "<h1>Paiements index</h1>",
            "no records found",
        ],
        INDEX_NOUVEAU
    ))
    print()

    print("-" * 70)
    print("3) templates/paiements/show.html.twig")
    print("-" * 70)
    resultats.append(remplacer_fichier_entier_verifie(
        racine,
        "templates/paiements/show.html.twig",
        [
            "{% block title %}Paiements{% endblock %}",
            "<h1>Paiements</h1>",
            "{{ include('paiements/_delete_form.html.twig') }}",
        ],
        SHOW_NOUVEAU
    ))
    print()

    print("-" * 70)
    print("4) templates/paiements/_delete_form.html.twig")
    print("-" * 70)
    resultats.append(remplacer_fichier_entier_verifie(
        racine,
        "templates/paiements/_delete_form.html.twig",
        [
            "Are you sure you want to delete this item?",
            "<button class=\"btn\">Delete</button>",
        ],
        DELETE_FORM_NOUVEAU
    ))
    print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Ouvrez Paiements dans le menu : chaque paiement affiche maintenant")
        print("son statut (En attente / Validé / Rejeté / Annulé). Sur un paiement")
        print("'En attente' (dont les chèques), un bouton Valider est disponible")
        print("directement dans la liste, et Valider/Rejeter en détail. Un paiement")
        print("Validé peut être Annulé (avec motif) depuis sa fiche.")
        print()
        print("Seuls les utilisateurs avec le role 'Encaisser des paiements'")
        print("peuvent valider/rejeter/annuler (comme pour créer un paiement).")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC]/[ABSENT] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
