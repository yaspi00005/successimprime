#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Livraison groupee :

1) Commande : la dimension (largeur x longueur en cm) est ajoutee/mise a
   jour automatiquement dans la designation a l'enregistrement.
2) Devis + Facture (PDF) : la remise par ligne est affichee dans une
   nouvelle colonne du tableau des travaux.
3) Liste des commandes : nouvelle colonne "Agent" (qui a enregistre la
   commande), recherche avancee gardee en session tant qu'elle n'est pas
   reinitialisee (?reset=1), et recherche dans les listes deroulantes du
   formulaire de recherche avancee (Select2).
4) Correction : client.nomComplet (prenom + nom) n'existait pas comme
   methode publique -> le prenom n'apparaissait nulle part (PDF, listes...).
   Utilise maintenant dans le nom du fichier PDF de facture telecharge.
5) Correction : le statut B2B du client n'etait jamais transmis au calcul
   des totaux d'une ligne de commande/devis (toujours traite comme B2C),
   ce qui empechait la remise/le tarif B2B de s'appliquer reellement a
   l'enregistrement.

Executer depuis la racine du projet :
    python3 livraison_dimension_remise_agent_session_b2b.py
"""

import sys


def appliquer(chemin, ancien, nouveau, label, occurrences_attendues=1):
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

    if occurrences != occurrences_attendues:
        print(
            f"[ERREUR] {label} : {occurrences} occurrence(s) trouvee(s) "
            f"dans {chemin} ({occurrences_attendues} attendue(s))"
        )
        return False

    contenu = contenu.replace(ancien, nouveau)

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)

    print(f"[OK] {label}")
    return True


resultats = []


# ============================================================
# 1) src/Entity/CommandesDetails.php
#    Dimension -> designation, a l'enregistrement.
# ============================================================

resultats.append(appliquer(
    "src/Entity/CommandesDetails.php",
    "            $this->calculerSurface();\n"
    "        }\n"
    "\n"
    "        $montantImpression = $this->calculerMontantImpression();",

    "            $this->calculerSurface();\n"
    "        }\n"
    "\n"
    "        $this->appliquerDimensionsALaDesignation();\n"
    "\n"
    "        $montantImpression = $this->calculerMontantImpression();",

    "1) CommandesDetails : appel appliquerDimensionsALaDesignation()",
))

resultats.append(appliquer(
    "src/Entity/CommandesDetails.php",
    "+ $montantTva;\n"
    "\n"
    "        return $this;\n"
    "    }\n"
    "\n"
    "    public function getProfilCouleurs(): ?string",

    "+ $montantTva;\n"
    "\n"
    "        return $this;\n"
    "    }\n"
    "\n"
    "    /**\n"
    "     * Ajoute (ou met à jour) les dimensions dans la désignation, au\n"
    "     * format \"Nom du produit (29,7 x 42 cm)\", pour qu'elles restent\n"
    "     * visibles partout où la désignation est affichée (listes, PDF)\n"
    "     * sans devoir modifier chaque gabarit.\n"
    "     *\n"
    "     * Idempotent : un ancien suffixe de dimensions est d'abord\n"
    "     * retiré avant d'ajouter le suffixe à jour, pour ne pas\n"
    "     * l'accumuler à chaque nouvel enregistrement.\n"
    "     */\n"
    "    private function appliquerDimensionsALaDesignation(): void\n"
    "    {\n"
    "        $base = preg_replace(\n"
    "            '/\\s*\\([0-9]+(?:,[0-9]+)?\\s*x\\s*[0-9]+(?:,[0-9]+)?\\s*cm\\)\\s*$/u',\n"
    "            '',\n"
    "            trim((string) $this->designation)\n"
    "        );\n"
    "\n"
    "        if (\n"
    "            $this->largeur === null\n"
    "            || $this->longueur === null\n"
    "        ) {\n"
    "            $this->designation = $base !== '' ? $base : null;\n"
    "\n"
    "            return;\n"
    "        }\n"
    "\n"
    "        $formaterCm = static function (string $valeurMetres): string {\n"
    "            $texte = number_format(\n"
    "                (float) $valeurMetres * 100,\n"
    "                2,\n"
    "                ',',\n"
    "                ''\n"
    "            );\n"
    "\n"
    "            $texte = rtrim($texte, '0');\n"
    "            $texte = rtrim($texte, ',');\n"
    "\n"
    "            return $texte === '' ? '0' : $texte;\n"
    "        };\n"
    "\n"
    "        $suffixe = sprintf(\n"
    "            ' (%s x %s cm)',\n"
    "            $formaterCm($this->largeur),\n"
    "            $formaterCm($this->longueur)\n"
    "        );\n"
    "\n"
    "        $this->designation = ($base !== '' ? $base : 'Produit') . $suffixe;\n"
    "    }\n"
    "\n"
    "    public function getProfilCouleurs(): ?string",

    "2) CommandesDetails : methode appliquerDimensionsALaDesignation()",
))


# ============================================================
# 2) templates/devis/pdf.html.twig et templates/factures/pdf.html.twig
#    Colonne Remise
# ============================================================

entete_ancien = (
    '\t\t\t\t\t<th style="width: 42%;">\n'
    '\t\t\t\t\t\tDésignation\n'
    '\t\t\t\t\t</th>\n'
    '\n'
    '\t\t\t\t\t<th style="width: 10%;">\n'
    '\t\t\t\t\t\tQté\n'
    '\t\t\t\t\t</th>\n'
    '\n'
    '\t\t\t\t\t<th style="width: 20%;">\n'
    '\t\t\t\t\t\tPrix unitaire\n'
    '\t\t\t\t\t</th>\n'
    '\n'
    '\t\t\t\t\t<th style="width: 23%;">\n'
    '\t\t\t\t\t\tTotal\n'
    '\t\t\t\t\t</th>'
)

entete_nouveau = (
    '\t\t\t\t\t<th style="width: 35%;">\n'
    '\t\t\t\t\t\tDésignation\n'
    '\t\t\t\t\t</th>\n'
    '\n'
    '\t\t\t\t\t<th style="width: 8%;">\n'
    '\t\t\t\t\t\tQté\n'
    '\t\t\t\t\t</th>\n'
    '\n'
    '\t\t\t\t\t<th style="width: 18%;">\n'
    '\t\t\t\t\t\tPrix unitaire\n'
    '\t\t\t\t\t</th>\n'
    '\n'
    '\t\t\t\t\t<th style="width: 10%;">\n'
    '\t\t\t\t\t\tRemise\n'
    '\t\t\t\t\t</th>\n'
    '\n'
    '\t\t\t\t\t<th style="width: 24%;">\n'
    '\t\t\t\t\t\tTotal\n'
    '\t\t\t\t\t</th>'
)

cellule_ancien = (
    'F CFA\n'
    '\n'
    '\t\t\t\t\t\t</td>\n'
    '\n'
    '\n'
    '\t\t\t\t\t\t<td class="\n'
    '\t\t\t\t\t\t\t\t                    text-right\n'
    '\t\t\t\t\t\t\t\t                    font-bold'
)

cellule_nouveau = (
    'F CFA\n'
    '\n'
    '\t\t\t\t\t\t</td>\n'
    '\n'
    '\n'
    '\t\t\t\t\t\t<td class="text-center">\n'
    '\n'
    '\t\t\t\t\t\t\t{% if detail.remise|default(0) > 0 %}\n'
    '\t\t\t\t\t\t\t\t{{\n'
    '                            detail.remise\n'
    '                            |number_format(2, \',\', \'\')\n'
    '                        }}\n'
    '\t\t\t\t\t\t\t\t%\n'
    '\t\t\t\t\t\t\t{% else %}\n'
    '\t\t\t\t\t\t\t\t—\n'
    '\t\t\t\t\t\t\t{% endif %}\n'
    '\n'
    '\t\t\t\t\t\t</td>\n'
    '\n'
    '\n'
    '\t\t\t\t\t\t<td class="\n'
    '\t\t\t\t\t\t\t\t                    text-right\n'
    '\t\t\t\t\t\t\t\t                    font-bold'
)

for fichier in ("templates/devis/pdf.html.twig", "templates/factures/pdf.html.twig"):
    resultats.append(appliquer(
        fichier, entete_ancien, entete_nouveau,
        f"3) {fichier} : entete colonne Remise",
    ))
    resultats.append(appliquer(
        fichier, cellule_ancien, cellule_nouveau,
        f"4) {fichier} : cellule Remise par ligne",
    ))
    resultats.append(appliquer(
        fichier,
        '<td colspan="5" class="text-center">',
        '<td colspan="6" class="text-center">',
        f"5) {fichier} : colspan etat vide",
    ))


# ============================================================
# 3) templates/commandes/index.html.twig
#    Colonne Agent + recherche en session + Select2
# ============================================================

fichier_index = "templates/commandes/index.html.twig"

resultats.append(appliquer(
    fichier_index,
    "{% set rechercheActive =\n"
    "        app.request.query.get('q')\n"
    "        or app.request.query.get('client')\n"
    "        or app.request.query.get('statut')\n"
    "        or app.request.query.get('etat')\n"
    "        or app.request.query.get('paiement')\n"
    "        or app.request.query.get('date_debut')\n"
    "        or app.request.query.get('date_fin')\n"
    "        or app.request.query.get('montant_min')\n"
    "        or app.request.query.get('montant_max')\n"
    "        or app.request.query.get('affichage') == 'toutes'\n"
    "    %}",

    "{% set rechercheActive =\n"
    "        filtres.q|default('')\n"
    "        or filtres.client|default('')\n"
    "        or filtres.statut|default('')\n"
    "        or filtres.etat|default('')\n"
    "        or filtres.paiement|default('')\n"
    "        or filtres.date_debut|default('')\n"
    "        or filtres.date_fin|default('')\n"
    "        or filtres.montant_min|default('')\n"
    "        or filtres.montant_max|default('')\n"
    "        or filtres.affichage|default('actives') == 'toutes'\n"
    "    %}",

    "6) index.html.twig : rechercheActive depuis filtres",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t<input type="search" name="q" class="form-control" value="{{ app.request.query.get(\'q\') }}" placeholder="N° commande, client, téléphone…">',
    '\t\t\t\t\t\t\t\t<input type="search" name="q" class="form-control" value="{{ filtres.q|default(\'\') }}" placeholder="N° commande, client, téléphone…">',
    "7) index.html.twig : champ q",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t\t<option value="{{ client.id }}" {{ app.request.query.get(\'client\') == client.id ? \'selected\' : \'\' }}>',
    '\t\t\t\t\t\t\t\t\t<option value="{{ client.id }}" {{ filtres.client|default(\'\') == client.id ? \'selected\' : \'\' }}>',
    "8) index.html.twig : select client",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t\t<option value="{{ statut.id }}" {{ app.request.query.get(\'statut\') == statut.id ? \'selected\' : \'\' }}>',
    '\t\t\t\t\t\t\t\t\t<option value="{{ statut.id }}" {{ filtres.statut|default(\'\') == statut.id ? \'selected\' : \'\' }}>',
    "9) index.html.twig : select statut",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t\t<option value="{{ etat.id }}" {{ app.request.query.get(\'etat\') == etat.id ? \'selected\' : \'\' }}>',
    '\t\t\t\t\t\t\t\t\t<option value="{{ etat.id }}" {{ filtres.etat|default(\'\') == etat.id ? \'selected\' : \'\' }}>',
    "10) index.html.twig : select etat",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t<option value="impayee" {{ app.request.query.get(\'paiement\') == \'impayee\' ? \'selected\' : \'\' }}>',
    '\t\t\t\t\t\t\t\t<option value="impayee" {{ filtres.paiement|default(\'\') == \'impayee\' ? \'selected\' : \'\' }}>',
    "11) index.html.twig : select paiement (impayee)",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t<option value="partielle" {{ app.request.query.get(\'paiement\') == \'partielle\' ? \'selected\' : \'\' }}>',
    '\t\t\t\t\t\t\t\t<option value="partielle" {{ filtres.paiement|default(\'\') == \'partielle\' ? \'selected\' : \'\' }}>',
    "12) index.html.twig : select paiement (partielle)",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t<option value="payee" {{ app.request.query.get(\'paiement\') == \'payee\' ? \'selected\' : \'\' }}>',
    '\t\t\t\t\t\t\t\t<option value="payee" {{ filtres.paiement|default(\'\') == \'payee\' ? \'selected\' : \'\' }}>',
    "13) index.html.twig : select paiement (payee)",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t\t<input type="date" name="date_debut" class="form-control" value="{{ app.request.query.get(\'date_debut\') }}">',
    '\t\t\t\t\t\t\t\t\t<input type="date" name="date_debut" class="form-control" value="{{ filtres.date_debut|default(\'\') }}">',
    "14) index.html.twig : champ date_debut",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t\t<input type="date" name="date_fin" class="form-control" value="{{ app.request.query.get(\'date_fin\') }}">',
    '\t\t\t\t\t\t\t\t\t<input type="date" name="date_fin" class="form-control" value="{{ filtres.date_fin|default(\'\') }}">',
    "15) index.html.twig : champ date_fin",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t\t<input type="number" min="0" name="montant_min" class="form-control" value="{{ app.request.query.get(\'montant_min\') }}" placeholder="0">',
    '\t\t\t\t\t\t\t\t\t<input type="number" min="0" name="montant_min" class="form-control" value="{{ filtres.montant_min|default(\'\') }}" placeholder="0">',
    "16) index.html.twig : champ montant_min",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t\t<input type="number" min="0" name="montant_max" class="form-control" value="{{ app.request.query.get(\'montant_max\') }}" placeholder="Illimité">',
    '\t\t\t\t\t\t\t\t\t<input type="number" min="0" name="montant_max" class="form-control" value="{{ filtres.montant_max|default(\'\') }}" placeholder="Illimité">',
    "17) index.html.twig : champ montant_max",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t<option value="actives" {{ app.request.query.get(\'affichage\', \'actives\') == \'actives\' ? \'selected\' : \'\' }}>',
    '\t\t\t\t\t\t\t\t<option value="actives" {{ filtres.affichage|default(\'actives\') == \'actives\' ? \'selected\' : \'\' }}>',
    "18) index.html.twig : select affichage (actives)",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t<option value="toutes" {{ app.request.query.get(\'affichage\') == \'toutes\' ? \'selected\' : \'\' }}>',
    '\t\t\t\t\t\t\t\t<option value="toutes" {{ filtres.affichage|default(\'\') == \'toutes\' ? \'selected\' : \'\' }}>',
    "19) index.html.twig : select affichage (toutes)",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t<option value="recent" {{ app.request.query.get(\'tri\') == \'recent\' ? \'selected\' : \'\' }}>Plus récentes</option>\n'
    '\t\t\t\t\t\t\t\t\t<option value="ancien" {{ app.request.query.get(\'tri\') == \'ancien\' ? \'selected\' : \'\' }}>Plus anciennes</option>\n'
    '\t\t\t\t\t\t\t\t\t<option value="montant_desc" {{ app.request.query.get(\'tri\') == \'montant_desc\' ? \'selected\' : \'\' }}>Montant décroissant</option>\n'
    '\t\t\t\t\t\t\t\t\t<option value="reste_desc" {{ app.request.query.get(\'tri\') == \'reste_desc\' ? \'selected\' : \'\' }}>Reste à payer décroissant</option>',

    '\t\t\t\t\t\t\t\t<option value="recent" {{ filtres.tri|default(\'recent\') == \'recent\' ? \'selected\' : \'\' }}>Plus récentes</option>\n'
    '\t\t\t\t\t\t\t\t\t<option value="ancien" {{ filtres.tri|default(\'\') == \'ancien\' ? \'selected\' : \'\' }}>Plus anciennes</option>\n'
    '\t\t\t\t\t\t\t\t\t<option value="montant_desc" {{ filtres.tri|default(\'\') == \'montant_desc\' ? \'selected\' : \'\' }}>Montant décroissant</option>\n'
    '\t\t\t\t\t\t\t\t\t<option value="reste_desc" {{ filtres.tri|default(\'\') == \'reste_desc\' ? \'selected\' : \'\' }}>Reste à payer décroissant</option>',

    "20) index.html.twig : select tri",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t<a href="{{ path(\'app_commandes_index\') }}" class="btn btn-light btn-block">',
    '\t\t\t\t\t\t<a href="{{ path(\'app_commandes_index\', {reset: 1}) }}" class="btn btn-light btn-block">',
    "21) index.html.twig : lien Reinitialiser",
))

resultats.append(appliquer(
    fichier_index,
    '<th scope="col">Client</th>',
    '<th scope="col">Client</th>\n\t\t\t\t\t\t\t\t\t<th scope="col">Agent</th>',
    "22) index.html.twig : entete colonne Agent",
))

resultats.append(appliquer(
    fichier_index,
    '{# 2. Client #}\n'
    '\t\t\t\t\t\t\t\t\t\t<td class="commande-client">\n'
    '\t\t\t\t\t\t\t\t\t\t\t<strong>\n'
    '\t\t\t\t\t\t\t\t\t\t\t\t{{ commande.clients }}\n'
    '\t\t\t\t\t\t\t\t\t\t\t</strong>\n'
    '\t\t\t\t\t\t\t\t\t\t</td>\n'
    '\n'
    '\t\t\t\t\t\t\t\t\t\t{# 3. Travaux #}',

    '{# 2. Client #}\n'
    '\t\t\t\t\t\t\t\t\t\t<td class="commande-client">\n'
    '\t\t\t\t\t\t\t\t\t\t\t<strong>\n'
    '\t\t\t\t\t\t\t\t\t\t\t\t{{ commande.clients }}\n'
    '\t\t\t\t\t\t\t\t\t\t\t</strong>\n'
    '\t\t\t\t\t\t\t\t\t\t</td>\n'
    '\n'
    '\t\t\t\t\t\t\t\t\t\t{# 2bis. Agent #}\n'
    '\t\t\t\t\t\t\t\t\t\t<td>\n'
    '\t\t\t\t\t\t\t\t\t\t\t{% if commande.agents %}\n'
    '\t\t\t\t\t\t\t\t\t\t\t\t{{ commande.agents.username }}\n'
    '\t\t\t\t\t\t\t\t\t\t\t{% else %}\n'
    '\t\t\t\t\t\t\t\t\t\t\t\t<span class="text-muted">—</span>\n'
    '\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n'
    '\t\t\t\t\t\t\t\t\t\t</td>\n'
    '\n'
    '\t\t\t\t\t\t\t\t\t\t{# 3. Travaux #}',

    "23) index.html.twig : cellule Agent",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t\t<td colspan="8">',
    '\t\t\t\t\t\t\t\t\t<td colspan="9">',
    "24) index.html.twig : colspan etat vide",
))

resultats.append(appliquer(
    fichier_index,
    '\t\t\t\t\t\t\t\t\t\t<a href="{{ path(\'app_commandes_index\') }}" class="btn btn-primary-light">',
    '\t\t\t\t\t\t\t\t\t\t<a href="{{ path(\'app_commandes_index\', {reset: 1}) }}" class="btn btn-primary-light">',
    "25) index.html.twig : lien Afficher les commandes actives",
))

resultats.append(appliquer(
    fichier_index,
    "ntLoaded', function () {\ndocument.querySelectorAll",
    "ntLoaded', function () {\n"
    "\n"
    "/*\n"
    " * Recherche dans les listes déroulantes du formulaire de\n"
    " * recherche avancée (client, statut, état...).\n"
    " */\n"
    "if (window.jQuery && window.jQuery.fn.select2) {\n"
    "window.jQuery('.commande-filter-card select.custom-select').select2({\n"
    "width: '100%'\n"
    "});\n"
    "}\n"
    "\n"
    "document.querySelectorAll",
    "26) index.html.twig : Select2 sur les listes deroulantes",
))


# ============================================================
# 4) src/Controller/CommandesController.php
#    Recherche gardee en session + statut B2B reellement transmis
# ============================================================

fichier_cc = "src/Controller/CommandesController.php"

resultats.append(appliquer(
    fichier_cc,
    "final class CommandesController extends AbstractController\n"
    "{\n"
    "    #[Route('/', name: 'app_commandes_index', methods: ['GET'])]\n"
    "    public function index(\n"
    "        Request $request,\n"
    "        CommandesRepository $commandesRepository,\n"
    "        ClientsRepository $clientsRepository\n"
    "    ): Response {\n"
    "        $filtres = [\n"
    "            'q' => trim((string) $request->query->get('q', '')),\n"
    "            'client' => (string) $request->query->get('client', ''),\n"
    "            'statut' => (string) $request->query->get('statut', ''),\n"
    "            'etat' => (string) $request->query->get('etat', ''),\n"
    "            'paiement' => (string) $request->query->get('paiement', ''),\n"
    "            'date_debut' => (string) $request->query->get('date_debut', ''),\n"
    "            'date_fin' => (string) $request->query->get('date_fin', ''),\n"
    "            'montant_min' => (string) $request->query->get('montant_min', ''),\n"
    "            'montant_max' => (string) $request->query->get('montant_max', ''),\n"
    "            'affichage' => (string) $request->query->get(\n"
    "                'affichage',\n"
    "                'actives'\n"
    "            ),\n"
    "            'tri' => (string) $request->query->get('tri', 'recent'),\n"
    "        ];\n"
    "\n"
    "        ",

    "final class CommandesController extends AbstractController\n"
    "{\n"
    "    private const CLES_FILTRES_COMMANDES = [\n"
    "        'q',\n"
    "        'client',\n"
    "        'statut',\n"
    "        'etat',\n"
    "        'paiement',\n"
    "        'date_debut',\n"
    "        'date_fin',\n"
    "        'montant_min',\n"
    "        'montant_max',\n"
    "        'affichage',\n"
    "        'tri',\n"
    "    ];\n"
    "\n"
    "    private const FILTRES_COMMANDES_PAR_DEFAUT = [\n"
    "        'q' => '',\n"
    "        'client' => '',\n"
    "        'statut' => '',\n"
    "        'etat' => '',\n"
    "        'paiement' => '',\n"
    "        'date_debut' => '',\n"
    "        'date_fin' => '',\n"
    "        'montant_min' => '',\n"
    "        'montant_max' => '',\n"
    "        'affichage' => 'actives',\n"
    "        'tri' => 'recent',\n"
    "    ];\n"
    "\n"
    "    #[Route('/', name: 'app_commandes_index', methods: ['GET'])]\n"
    "    public function index(\n"
    "        Request $request,\n"
    "        CommandesRepository $commandesRepository,\n"
    "        ClientsRepository $clientsRepository\n"
    "    ): Response {\n"
    "        $session = $request->getSession();\n"
    "\n"
    "        /*\n"
    "     * ============================================================\n"
    "     * RECHERCHE GARDÉE EN SESSION\n"
    "     * ============================================================\n"
    "     *\n"
    "     * Tant qu'aucune recherche n'a été explicitement réinitialisée\n"
    "     * (bouton \"Réinitialiser\", ?reset=1), on retrouve les derniers\n"
    "     * filtres appliqués même en revenant sur la liste sans\n"
    "     * paramètre d'URL (ex. via le menu).\n"
    "     */\n"
    "        if ($request->query->getBoolean('reset')) {\n"
    "            $session->remove('commandes_filtres');\n"
    "        }\n"
    "\n"
    "        $requeteContientUnFiltre = false;\n"
    "\n"
    "        foreach (self::CLES_FILTRES_COMMANDES as $cle) {\n"
    "            if ($request->query->get($cle) !== null) {\n"
    "                $requeteContientUnFiltre = true;\n"
    "\n"
    "                break;\n"
    "            }\n"
    "        }\n"
    "\n"
    "        if ($requeteContientUnFiltre) {\n"
    "            $filtres = [\n"
    "                'q' => trim((string) $request->query->get('q', '')),\n"
    "                'client' => (string) $request->query->get('client', ''),\n"
    "                'statut' => (string) $request->query->get('statut', ''),\n"
    "                'etat' => (string) $request->query->get('etat', ''),\n"
    "                'paiement' => (string) $request->query->get('paiement', ''),\n"
    "                'date_debut' => (string) $request->query->get('date_debut', ''),\n"
    "                'date_fin' => (string) $request->query->get('date_fin', ''),\n"
    "                'montant_min' => (string) $request->query->get('montant_min', ''),\n"
    "                'montant_max' => (string) $request->query->get('montant_max', ''),\n"
    "                'affichage' => (string) $request->query->get(\n"
    "                    'affichage',\n"
    "                    'actives'\n"
    "                ),\n"
    "                'tri' => (string) $request->query->get('tri', 'recent'),\n"
    "            ];\n"
    "\n"
    "            $session->set('commandes_filtres', $filtres);\n"
    "        } else {\n"
    "            $filtres = $session->get(\n"
    "                'commandes_filtres',\n"
    "                self::FILTRES_COMMANDES_PAR_DEFAUT\n"
    "            );\n"
    "        }\n"
    "\n"
    "        ",

    "27) CommandesController : recherche en session (index)",
))

resultats.append(appliquer(
    fichier_cc,
    "        $detailsForm =\n"
    "            $form->get('commandesDetails');\n"
    "\n"
    "        foreach ($detailsForm as $detailForm) {",

    "        $detailsForm =\n"
    "            $form->get('commandesDetails');\n"
    "\n"
    "        $clientB2B =\n"
    "            $commande->getClients()?->isB2B()\n"
    "            ?? false;\n"
    "\n"
    "        foreach ($detailsForm as $detailForm) {",

    "28) CommandesController : statut B2B reel du client",
))

resultats.append(appliquer(
    fichier_cc,
    "                $detail->calculerTotaux(\n"
    "                    false\n"
    "                );",

    "                $detail->calculerTotaux(\n"
    "                    $clientB2B\n"
    "                );",

    "29) CommandesController : calculerTotaux($clientB2B) x2",
    2,
))

resultats.append(appliquer(
    fichier_cc,
    "            $detail->calculerTotaux(\n"
    "                false\n"
    "            );",

    "            $detail->calculerTotaux(\n"
    "                $clientB2B\n"
    "            );",

    "30) CommandesController : calculerTotaux($clientB2B) ligne produit",
))


# ============================================================
# 5) src/Controller/DevisController.php
#    Statut B2B reellement transmis (meme correction que commande)
# ============================================================

fichier_dc = "src/Controller/DevisController.php"

resultats.append(appliquer(
    fichier_dc,
    "    $detailsForm =\n"
    "        $form->get('devisDetails');\n"
    "\n"
    "    foreach ($detailsForm as $detailForm) {",

    "    $detailsForm =\n"
    "        $form->get('devisDetails');\n"
    "\n"
    "    $clientB2B =\n"
    "        $devi->getClients()?->isB2B()\n"
    "        ?? false;\n"
    "\n"
    "    foreach ($detailsForm as $detailForm) {",

    "31) DevisController : statut B2B reel du client",
))

resultats.append(appliquer(
    fichier_dc,
    "            $detail->calculerTotaux(\n"
    "                false\n"
    "            );",

    "            $detail->calculerTotaux(\n"
    "                $clientB2B\n"
    "            );",

    "32) DevisController : calculerTotaux($clientB2B) x2",
    2,
))

resultats.append(appliquer(
    fichier_dc,
    "        $detail->calculerTotaux(\n"
    "            false\n"
    "        );",

    "        $detail->calculerTotaux(\n"
    "            $clientB2B\n"
    "        );",

    "33) DevisController : calculerTotaux($clientB2B) ligne produit",
))


# ============================================================
# 6) src/Entity/Clients.php
#    client.nomComplet (prenom + nom) manquant
# ============================================================

resultats.append(appliquer(
    "src/Entity/Clients.php",
    "    public function __toString(): string\n"
    "    {\n"
    "        if (\n"
    "            $this->isEntreprise()\n"
    "            && $this->raisonSociale !== null\n"
    "        ) {\n"
    "            return $this->raisonSociale;\n"
    "        }\n"
    "\n"
    "        $nomComplet = trim(sprintf(\n"
    "            '%s %s',\n"
    "            $this->prenom ?? '',\n"
    "            $this->nom ?? ''\n"
    "        ));\n"
    "\n"
    "        return $nomComplet !== ''\n"
    "            ? $nomComplet\n"
    "            : ($this->code ?? 'Client');\n"
    "    }\n"
    "\n"
    "    private function normaliserValeur(",

    "    /*\n"
    "     * De nombreux templates appellent client.nomComplet en\n"
    "     * s'attendant à un accesseur public (avec repli sur client.nom\n"
    "     * si absent). Comme cette méthode n'existait pas, Twig\n"
    "     * résolvait toujours silencieusement vers le repli, et le\n"
    "     * prénom n'apparaissait donc jamais nulle part (PDF, listes...).\n"
    "     */\n"
    "    public function getNomComplet(): string\n"
    "    {\n"
    "        if (\n"
    "            $this->isEntreprise()\n"
    "            && $this->raisonSociale !== null\n"
    "        ) {\n"
    "            return $this->raisonSociale;\n"
    "        }\n"
    "\n"
    "        $nomComplet = trim(sprintf(\n"
    "            '%s %s',\n"
    "            $this->prenom ?? '',\n"
    "            $this->nom ?? ''\n"
    "        ));\n"
    "\n"
    "        return $nomComplet !== ''\n"
    "            ? $nomComplet\n"
    "            : ($this->code ?? 'Client');\n"
    "    }\n"
    "\n"
    "    public function __toString(): string\n"
    "    {\n"
    "        return $this->getNomComplet();\n"
    "    }\n"
    "\n"
    "    private function normaliserValeur(",

    "34) Clients : ajoute getNomComplet()",
))


# ============================================================
# 7) src/Controller/FacturesController.php
#    Prenom + nom du client dans le nom du PDF telecharge
# ============================================================

fichier_fc = "src/Controller/FacturesController.php"

resultats.append(appliquer(
    fichier_fc,
    "                    'Content-Disposition' =>\n"
    "                        sprintf(\n"
    "                            'inline; filename=\"%s.pdf\"',\n"
    "                            $numero\n"
    "                        ),",

    "                    'Content-Disposition' =>\n"
    "                        sprintf(\n"
    "                            'inline; filename=\"%s%s.pdf\"',\n"
    "                            $numero,\n"
    "                            $this->suffixeNomClientPdf($facture)\n"
    "                        ),",

    "35) FacturesController : nom client dans le PDF archive",
))

resultats.append(appliquer(
    fichier_fc,
    "    private function imageVersDataUri(\n"
    "        string $chemin\n"
    "    ): ?string {",

    "    private function suffixeNomClientPdf(\n"
    "        Factures $facture\n"
    "    ): string {\n"
    "        $client =\n"
    "            $facture->getCommande()\n"
    "                ?->getClients();\n"
    "\n"
    "        if ($client === null) {\n"
    "            return '';\n"
    "        }\n"
    "\n"
    "        $nom =\n"
    "            preg_replace(\n"
    "                '/[^A-Za-z0-9\\-_]/',\n"
    "                '-',\n"
    "                $client->getNomComplet()\n"
    "            );\n"
    "\n"
    "        $nom =\n"
    "            trim(\n"
    "                (string) $nom,\n"
    "                '-'\n"
    "            );\n"
    "\n"
    "        return $nom !== ''\n"
    "            ? '_' . $nom\n"
    "            : '';\n"
    "    }\n"
    "\n"
    "    private function imageVersDataUri(\n"
    "        string $chemin\n"
    "    ): ?string {",

    "36) FacturesController : methode suffixeNomClientPdf()",
))

resultats.append(appliquer(
    fichier_fc,
    "    $nomFichier =\n"
    "        $numeroNettoye\n"
    "        . '.pdf';",

    "    $nomFichier =\n"
    "        $numeroNettoye\n"
    "        . '.pdf';\n"
    "\n"
    "\n"
    "    $nomTelechargement =\n"
    "        $numeroNettoye\n"
    "        . $this->suffixeNomClientPdf(\n"
    "            $facture\n"
    "        )\n"
    "        . '.pdf';",

    "37) FacturesController : nomTelechargement (nouveau PDF)",
))

resultats.append(appliquer(
    fichier_fc,
    "            'Content-Disposition' =>\n"
    "                sprintf(\n"
    "                    'inline; filename=\"%s\"',\n"
    "                    $nomFichier\n"
    "                ),",

    "            'Content-Disposition' =>\n"
    "                sprintf(\n"
    "                    'inline; filename=\"%s\"',\n"
    "                    $nomTelechargement\n"
    "                ),",

    "38) FacturesController : nom client dans le PDF fraichement genere",
))


# ============================================================
# Bilan
# ============================================================

echecs = resultats.count(False)

print()
if echecs:
    print(f"Termine avec {echecs} erreur(s). Voir les [ERREUR] ci-dessus.")
    sys.exit(1)
else:
    print("Termine sans erreur.")
