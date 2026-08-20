#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige le PDF de facture qui reste bloque sur l'ancien "reste a payer"
meme apres un paiement complet.

Cause : une fois genere, le PDF est archive sur le disque, et la route
de telechargement/visualisation renvoie TOUJOURS ce fichier archive sans
le regenerer -- meme si un paiement est enregistre entre-temps ou que la
facture est "actualisee" depuis la commande. Le montant paye / reste a
payer est pourtant correctement recalcule en base, mais jamais reporte
sur le PDF deja genere.

Correction : quand le montant paye change reellement (nouveau paiement),
ou quand la facture est actualisee depuis la commande, l'ancien PDF
archive est invalide en base. La prochaine consultation/telechargement
regenere alors automatiquement un PDF a jour (les montants factures
restent, eux, inchanges -- seule la situation de paiement est rafraichie).

Executer depuis la racine du projet :
    python3 fix_pdf_facture_reste_a_payer_fige.py
"""

import sys


def appliquer(chemin, ancien, nouveau, label):
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()
    except FileNotFoundError:
        print(f"[ERREUR] Fichier introuvable : {chemin}")
        return False

    if nouveau in contenu:
        print(f"[SKIP] {label} : deja applique.")
        return True

    occurrences = contenu.count(ancien)

    if occurrences != 1:
        print(
            f"[ERREUR] {label} : {occurrences} occurrence(s) trouvee(s) "
            f"dans {chemin} (1 attendue)"
        )
        return False

    contenu = contenu.replace(ancien, nouveau)

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)

    print(f"[OK] {label}")
    return True


resultats = []

fichier = "src/Entity/Factures.php"

# 1) chargerDepuisCommande() : invalide le PDF archive quand la facture
#    est actualisee depuis la commande (bouton "Actualiser").
resultats.append(appliquer(
    fichier,
    "$this->montantTva =\n"
    "            max(\n"
    "                0,\n"
    "                $commandeTtc\n"
    "                - max(\n"
    "                    0,\n"
    "                    $this->totalHt\n"
    "                    - $this->remise\n"
    "                )\n"
    "            );\n"
    "\n"
    "        $this->recalculerTotal();\n"
    "\n"
    "        return $this;\n"
    "    }",

    "$this->montantTva =\n"
    "            max(\n"
    "                0,\n"
    "                $commandeTtc\n"
    "                - max(\n"
    "                    0,\n"
    "                    $this->totalHt\n"
    "                    - $this->remise\n"
    "                )\n"
    "            );\n"
    "\n"
    "        $this->recalculerTotal();\n"
    "\n"
    "        /*\n"
    "         * Les montants viennent d'être rechargés depuis la\n"
    "         * commande (bouton \"Actualiser\") : un éventuel PDF déjà\n"
    "         * archivé afficherait des montants obsolètes. On\n"
    "         * l'invalide pour forcer une régénération à la prochaine\n"
    "         * consultation.\n"
    "         */\n"
    "        $this->pdfFichier = null;\n"
    "        $this->pdfHash = null;\n"
    "        $this->pdfGenereLe = null;\n"
    "\n"
    "        return $this;\n"
    "    }",

    "1) Factures : invalide le PDF archive lors d'une actualisation",
))

# 2) synchroniserPaiementsDepuisCommande() : memorise le montant paye
#    avant recalcul, pour savoir s'il a reellement change.
resultats.append(appliquer(
    fichier,
    "if (\n"
    "        !$this->comptabilisee\n"
    "        || $this->commande === null\n"
    "    ) {\n"
    "        return $this;\n"
    "    }\n"
    "\n"
    "    $totalPaye = 0;",

    "if (\n"
    "        !$this->comptabilisee\n"
    "        || $this->commande === null\n"
    "    ) {\n"
    "        return $this;\n"
    "    }\n"
    "\n"
    "    $montantPayeAvant = $this->montantPaye;\n"
    "\n"
    "    $totalPaye = 0;",

    "2) Factures : memorise le montant paye avant recalcul",
))

# 3) synchroniserPaiementsDepuisCommande() : invalide le PDF archive
#    uniquement si le montant paye a reellement change (pas a chaque
#    simple consultation de la facture).
resultats.append(appliquer(
    fichier,
    "self::STATUT_PARTIELLE;\n"
    "\n"
    "    } else {\n"
    "\n"
    "        $this->statutPaiement =\n"
    "            self::STATUT_IMPAYEE;\n"
    "    }\n"
    "\n"
    "\n"
    "    return $this;\n"
    "}\n"
    "\n"
    "\n"
    "    /*\n"
    "     * ============================================================\n"
    "     * LIFECYCLE",

    "self::STATUT_PARTIELLE;\n"
    "\n"
    "    } else {\n"
    "\n"
    "        $this->statutPaiement =\n"
    "            self::STATUT_IMPAYEE;\n"
    "    }\n"
    "\n"
    "\n"
    "    /*\n"
    "     * Le PDF déjà archivé affiche un \"reste à payer\" figé au\n"
    "     * moment de sa génération. Si le montant payé vient\n"
    "     * réellement de changer, l'ancien PDF est invalidé : la\n"
    "     * prochaine consultation en régénère un à jour (les montants\n"
    "     * facturés, eux, restent inchangés). Sans ce test, la simple\n"
    "     * consultation de la facture (qui appelle cette méthode à\n"
    "     * chaque affichage) forcerait une régénération à chaque fois.\n"
    "     */\n"
    "    if ($this->montantPaye !== $montantPayeAvant) {\n"
    "        $this->pdfFichier = null;\n"
    "        $this->pdfHash = null;\n"
    "        $this->pdfGenereLe = null;\n"
    "    }\n"
    "\n"
    "\n"
    "    return $this;\n"
    "}\n"
    "\n"
    "\n"
    "    /*\n"
    "     * ============================================================\n"
    "     * LIFECYCLE",

    "3) Factures : invalide le PDF archive quand le paiement change",
))


echecs = resultats.count(False)

print()
if echecs:
    print(f"Termine avec {echecs} erreur(s). Voir les [ERREUR] ci-dessus.")
    sys.exit(1)
else:
    print("Termine sans erreur.")
