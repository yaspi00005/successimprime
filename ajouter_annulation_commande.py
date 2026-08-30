#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute la possibilite d'annuler une commande :

  - tant que la production/livraison n'a pas commence, n'importe quel
    utilisateur ROLE_COMMANDE peut annuler la commande ;
  - une fois le circuit commence (meme si la production est
    terminee), seul un administrateur peut encore annuler ET modifier
    la commande (y compris ses lignes).

Choix assume (valide avec vous) : l'annulation ne recredite pas
automatiquement le stock deja consomme, ne touche pas aux factures ni
aux paiements existants -- comme le fait deja l'annulation d'un ordre
de production termine dans l'application. Un avertissement est
affiche si du stock avait deja ete consomme.

Modifie 2 fichiers :
  - src/Controller/CommandesController.php
  - templates/commandes/show.html.twig

Usage:
    python3 ajouter_annulation_commande.py /chemin/vers/successImprim
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


def ajouter_a_la_fin_verifie(racine, chemin_relatif, marqueur, suffixe_attendu, texte_a_ajouter):
    """
    Ajoute `texte_a_ajouter` a la toute fin du fichier, seulement si
    le fichier se termine bien par `suffixe_attendu` (sinon, on ne
    devine pas ou l'inserer -> abandon sans rien ecrire).
    """
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
# 1) src/Controller/CommandesController.php
# ============================================================

CTRL_BLOC_A_ANCIEN = """                /*
             * ========================================================
             * ADMIN + CIRCUIT DÉJÀ COMMENCÉ
             * ========================================================
             *
             * Même pour l'admin, on conserve les contrôles métier
             * existants si nécessaire.
             */
                if ($circuitDejaCommence) {"""

CTRL_BLOC_A_NOUVEAU = """                /*
             * ========================================================
             * CIRCUIT DÉJÀ COMMENCÉ
             * ========================================================
             *
             * Un admin peut modifier les lignes même après le
             * démarrage de la production/livraison ; un utilisateur
             * non-admin reste bloqué sur les changements structurels.
             */
                if ($circuitDejaCommence && !$this->isGranted('ROLE_ADMIN')) {"""

CTRL_BLOC_B_ANCIEN = """        if (!$user instanceof User) {
            throw $this->createAccessDeniedException(
                'Vous devez être connecté pour modifier une commande.'
            );
        }


        /*
     * ============================================================
     * ÉTAT AVANT MODIFICATION
     * ============================================================
     */
        $commandeEtaitValidee ="""

CTRL_BLOC_B_NOUVEAU = '        if (!$user instanceof User) {\n            throw $this->createAccessDeniedException(\n                \'Vous devez être connecté pour modifier une commande.\'\n            );\n        }\n\n\n        /*\n     * ============================================================\n     * COMMANDE ANNULÉE\n     * ============================================================\n     *\n     * Une commande annulée n\'a plus lieu d\'être modifiée, même par\n     * un administrateur : ses lignes ne sont plus "en circuit"\n     * (elles sont toutes PRODUCTION_ANNULEE), donc le verrouillage\n     * ci-dessous ne suffirait pas seul à la protéger.\n     */\n        if ($commande->getStatutTravaux() === \'annulee\') {\n\n            $this->addFlash(\n                \'error\',\n                \'Cette commande est annulée et ne peut plus être modifiée.\'\n            );\n\n            return $this->redirectToRoute(\n                \'app_commandes_show\',\n                [\n                    \'id\' =>\n                    $commande->getId(),\n                ],\n                Response::HTTP_SEE_OTHER\n            );\n        }\n\n\n        /*\n     * ============================================================\n     * ÉTAT AVANT MODIFICATION\n     * ============================================================\n     */\n'

CTRL_MARQUEUR = "COMMANDE ANNULÉE"


CTRL_BLOC_C_ANCIEN = """        return $this->redirectToRoute('app_commandes_index', [], Response::HTTP_SEE_OTHER);
    }"""

CTRL_BLOC_C_NOUVEAU = '        return $this->redirectToRoute(\'app_commandes_index\', [], Response::HTTP_SEE_OTHER);\n    }\n\n    /**\n     * Annule une commande : tant que la production/livraison n\'a pas\n     * commencé, n\'importe quel utilisateur ROLE_COMMANDE peut le\n     * faire ; une fois le circuit commencé (même terminé/livré),\n     * seul un administrateur le peut encore.\n     *\n     * Choix assumé : aucune reprise automatique du stock déjà\n     * consommé, des factures ou des paiements existants — comme pour\n     * l\'annulation d\'un ordre de production déjà terminé, on se\n     * contente de tracer le fait et de prévenir l\'utilisateur ;\n     * les régularisations éventuelles restent manuelles.\n     */\n    #[Route(\'/{id}/annuler\', name: \'app_commandes_annuler\', methods: [\'POST\'])]\n    public function annuler(Request $request, Commandes $commande, EntityManagerInterface $entityManager): Response\n    {\n        $user = $this->getUser();\n\n        if (!$user instanceof User) {\n            throw $this->createAccessDeniedException(\'Vous devez être connecté pour annuler une commande.\');\n        }\n\n        if (!$this->isCsrfTokenValid(\'annuler-commande-\' . $commande->getId(), $request->getPayload()->getString(\'_token\'))) {\n            $this->addFlash(\'error\', \'Jeton de sécurité invalide.\');\n\n            return $this->redirectToRoute(\'app_commandes_show\', [\'id\' => $commande->getId()], Response::HTTP_SEE_OTHER);\n        }\n\n        if ($commande->getStatutTravaux() === \'annulee\') {\n            $this->addFlash(\'warning\', \'Cette commande est déjà annulée.\');\n\n            return $this->redirectToRoute(\'app_commandes_show\', [\'id\' => $commande->getId()], Response::HTTP_SEE_OTHER);\n        }\n\n        if ($this->commandeACommenceSonCircuit($commande) && !$this->isGranted(\'ROLE_ADMIN\')) {\n            $this->addFlash(\n                \'error\',\n                \'Cette commande a déjà commencé sa production ou sa livraison. Seul un administrateur peut encore l’annuler.\'\n            );\n\n            return $this->redirectToRoute(\'app_commandes_show\', [\'id\' => $commande->getId()], Response::HTTP_SEE_OTHER);\n        }\n\n        $stockDejaConsomme = false;\n\n        foreach ($commande->getCommandesDetails() as $detail) {\n            if (!$detail instanceof CommandesDetails) {\n                continue;\n            }\n\n            if (\n                in_array(\n                    $detail->getStatutProduction(),\n                    [\n                        CommandesDetails::PRODUCTION_TERMINEE,\n                        CommandesDetails::PRODUCTION_PRETE_LIVRAISON,\n                        CommandesDetails::PRODUCTION_EN_LIVRAISON,\n                        CommandesDetails::PRODUCTION_LIVREE,\n                    ],\n                    true\n                )\n            ) {\n                $stockDejaConsomme = true;\n            }\n\n            $detail->setStatutProduction(CommandesDetails::PRODUCTION_ANNULEE);\n        }\n\n        $note = sprintf(\n            \'[Commande annulée le %s par %s]\',\n            (new \\DateTimeImmutable())->format(\'d/m/Y H:i\'),\n            $user->getUserIdentifier()\n        );\n\n        $observationExistante = $commande->getObservation();\n        $commande->setObservation(\n            $observationExistante !== null && trim($observationExistante) !== \'\'\n                ? $observationExistante . "\\n\\n" . $note\n                : $note\n        );\n\n        $entityManager->flush();\n\n        $message = sprintf(\'La commande %s a été annulée.\', $commande->getNumero() ?? (\'#\' . $commande->getId()));\n\n        if ($stockDejaConsomme) {\n            $message .= \' Attention : du stock avait déjà été consommé pour cette commande et n’a pas été recrédité automatiquement.\';\n        }\n\n        $this->addFlash(\'success\', $message);\n\n        return $this->redirectToRoute(\'app_commandes_show\', [\'id\' => $commande->getId()], Response::HTTP_SEE_OTHER);\n    }'


# ============================================================
# 2) templates/commandes/show.html.twig
# ============================================================

TWIG_BLOC_MODIFIER_ANCIEN = '\t\t\t\t{# ====================================================\n\t\t\t\t\t\t\t\t   MODIFIER\n\t\t\t\t\t\t\t\t   ==================================================== #}\n\n\t\t\t\t{% if\n\t\t\t\t\tpeutModifierCommande\n\t\t\t\t\tand (\n\t\t\t\t\t\tnot commandeVerrouilleeProduction\n\t\t\t\t\t\tor estAdmin\n\t\t\t\t\t)\n\t\t\t\t%}\n\n\t\t\t\t\t<a href="{{ path( \'app_commandes_edit\', { id: commande.id } ) }}" class="btn btn-sm btn-primary mr-2 mb-2">\n\t\t\t\t\t\t<i class="fe fe-edit-2 mr-1"></i>\n\n\t\t\t\t\t\tModifier\n\t\t\t\t\t</a>\n\n\t\t\t\t{% elseif\n\t\t\t\t\tcommandeVerrouilleeProduction\n\t\t\t\t\tand not estAdmin\n\t\t\t\t%}\n\n\t\t\t\t\t<button type="button" class="btn btn-sm btn-secondary mr-2 mb-2" disabled title="La production a déjà démarré">\n\t\t\t\t\t\t<i class="fa fa-lock mr-1"></i>\n\n\t\t\t\t\t\tCommande verrouillée\n\t\t\t\t\t</button>\n\n\t\t\t\t{% endif %}'
TWIG_BLOC_MODIFIER_NOUVEAU = '\t\t\t\t{# ====================================================\n\t\t\t\t\t\t\t\t   MODIFIER\n\t\t\t\t\t\t\t\t   ==================================================== #}\n\n\t\t\t\t{% if\n\t\t\t\t\tpeutModifierCommande\n\t\t\t\t\tand commande.statutTravaux != \'annulee\'\n\t\t\t\t\tand (\n\t\t\t\t\t\tnot commandeVerrouilleeProduction\n\t\t\t\t\t\tor estAdmin\n\t\t\t\t\t)\n\t\t\t\t%}\n\n\t\t\t\t\t<a href="{{ path( \'app_commandes_edit\', { id: commande.id } ) }}" class="btn btn-sm btn-primary mr-2 mb-2">\n\t\t\t\t\t\t<i class="fe fe-edit-2 mr-1"></i>\n\n\t\t\t\t\t\tModifier\n\t\t\t\t\t</a>\n\n\t\t\t\t{% elseif\n\t\t\t\t\tcommandeVerrouilleeProduction\n\t\t\t\t\tand not estAdmin\n\t\t\t\t\tand commande.statutTravaux != \'annulee\'\n\t\t\t\t%}\n\n\t\t\t\t\t<button type="button" class="btn btn-sm btn-secondary mr-2 mb-2" disabled title="La production a déjà démarré">\n\t\t\t\t\t\t<i class="fa fa-lock mr-1"></i>\n\n\t\t\t\t\t\tCommande verrouillée\n\t\t\t\t\t</button>\n\n\t\t\t\t{% endif %}'

TWIG_BLOC_ANNULER_ANCIEN = '\t\t\t\t{# ====================================================\n\t\t\t\t\t\t\t\t   SUPPRIMER (ADMIN)\n\t\t\t\t\t\t\t\t   ==================================================== #}\n\n\t\t\t\t{% if estAdmin %}\n\n\t\t\t\t\t<form method="post" action="{{ path( \'app_commandes_delete\', { id: commande.id } ) }}" class="js-confirm-form d-inline" data-message="Supprimer définitivement la commande {{ commande.numero }} ? Cette action est irréversible.">\n\n\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token( \'delete\' ~ commande.id ) }}">\n\n\t\t\t\t\t\t<button type="submit" class="btn btn-sm btn-danger mr-2 mb-2">\n\t\t\t\t\t\t\t<i class="fe fe-trash-2 mr-1"></i>\n\n\t\t\t\t\t\t\tSupprimer\n\t\t\t\t\t\t</button>\n\n\t\t\t\t\t</form>\n\n\t\t\t\t{% endif %}'
TWIG_BLOC_ANNULER_NOUVEAU = '\t\t\t\t{# ====================================================\n\t\t\t\t\t\t\t\t   SUPPRIMER (ADMIN)\n\t\t\t\t\t\t\t\t   ==================================================== #}\n\n\t\t\t\t{% if estAdmin %}\n\n\t\t\t\t\t<form method="post" action="{{ path( \'app_commandes_delete\', { id: commande.id } ) }}" class="js-confirm-form d-inline" data-message="Supprimer définitivement la commande {{ commande.numero }} ? Cette action est irréversible.">\n\n\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token( \'delete\' ~ commande.id ) }}">\n\n\t\t\t\t\t\t<button type="submit" class="btn btn-sm btn-danger mr-2 mb-2">\n\t\t\t\t\t\t\t<i class="fe fe-trash-2 mr-1"></i>\n\n\t\t\t\t\t\t\tSupprimer\n\t\t\t\t\t\t</button>\n\n\t\t\t\t\t</form>\n\n\t\t\t\t{% endif %}\n\n\n\t\t\t\t{# ====================================================\n\t\t\t\t\t\t\t\t   ANNULER LA COMMANDE\n\t\t\t\t\t\t\t\t   ==================================================== #}\n\n\t\t\t\t{% if\n\t\t\t\t\tpeutModifierCommande\n\t\t\t\t\tand commande.statutTravaux != \'annulee\'\n\t\t\t\t\tand (\n\t\t\t\t\t\tnot commandeVerrouilleeProduction\n\t\t\t\t\t\tor estAdmin\n\t\t\t\t\t)\n\t\t\t\t%}\n\n\t\t\t\t\t<form method="post" action="{{ path( \'app_commandes_annuler\', { id: commande.id } ) }}" class="js-confirm-form d-inline" data-message="Annuler la commande {{ commande.numero }} ? Cette action est irréversible.">\n\n\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token( \'annuler-commande-\' ~ commande.id ) }}">\n\n\t\t\t\t\t\t<button type="submit" class="btn btn-sm btn-outline-danger mr-2 mb-2">\n\t\t\t\t\t\t\t<i class="fe fe-x-circle mr-1"></i>\n\n\t\t\t\t\t\t\tAnnuler la commande\n\t\t\t\t\t\t</button>\n\n\t\t\t\t\t</form>\n\n\t\t\t\t{% endif %}'

TWIG_BLOC_JS_NOUVEAU = "\n\n\n{% block javascripts %}\n\n\t{{ parent() }}\n\n\t<script>\n\t\tdocument.addEventListener('DOMContentLoaded', function () {\n\n\t\t\tconst formulaires = document.querySelectorAll('.js-confirm-form');\n\n\t\t\tformulaires.forEach(function (formulaire) {\n\n\t\t\t\tformulaire.addEventListener('submit', function (event) {\n\n\t\t\t\t\tconst message = formulaire.dataset.message || 'Voulez-vous continuer ?';\n\n\t\t\t\t\tif (!window.confirm(message)) {\n\t\t\t\t\t\tevent.preventDefault();\n\t\t\t\t\t}\n\n\t\t\t\t});\n\n\t\t\t});\n\n\t\t});\n\t</script>\n\n{% endblock %}\n"

TWIG_MARQUEUR = "app_commandes_annuler"


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    if not PHP_LINT_DISPONIBLE:
        print("(info : commande 'php' introuvable ici, le controle 'php -l' sera saute)")
        print()

    resultats = []

    print("-" * 70)
    print("1) src/Controller/CommandesController.php")
    print("-" * 70)
    resultats.append(appliquer_blocs_verifie(
        racine,
        "src/Controller/CommandesController.php",
        CTRL_MARQUEUR,
        [
            (CTRL_BLOC_A_ANCIEN, CTRL_BLOC_A_NOUVEAU),
            (CTRL_BLOC_B_ANCIEN, CTRL_BLOC_B_NOUVEAU),
            (CTRL_BLOC_C_ANCIEN, CTRL_BLOC_C_NOUVEAU),
        ]
    ))
    print()

    print("-" * 70)
    print("2) templates/commandes/show.html.twig")
    print("-" * 70)
    resultat_twig = appliquer_blocs_verifie(
        racine,
        "templates/commandes/show.html.twig",
        TWIG_MARQUEUR,
        [
            (TWIG_BLOC_MODIFIER_ANCIEN, TWIG_BLOC_MODIFIER_NOUVEAU),
            (TWIG_BLOC_ANNULER_ANCIEN, TWIG_BLOC_ANNULER_NOUVEAU),
        ]
    )
    if resultat_twig:
        resultat_twig = ajouter_a_la_fin_verifie(
            racine,
            "templates/commandes/show.html.twig",
            "querySelectorAll('.js-confirm-form')",
            "\t</style>\n\n{% endblock %}",
            TWIG_BLOC_JS_NOUVEAU
        )
    resultats.append(resultat_twig)
    print()

    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Sur la fiche d'une commande :")
        print("- un bouton 'Annuler la commande' apparait tant que la")
        print("  production n'a pas commence (visible pour tout utilisateur")
        print("  ROLE_COMMANDE) ;")
        print("- une fois la production/livraison commencee (meme terminee),")
        print("  seul un administrateur voit encore ce bouton, et peut aussi")
        print("  modifier les lignes de la commande via 'Modifier'.")
        print()
        print("NB : annuler ne recredite pas automatiquement le stock deja")
        print("consomme ni ne touche aux factures/paiements existants -- un")
        print("message avertit l'administrateur si du stock avait deja ete")
        print("consomme, a corriger manuellement si besoin.")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
