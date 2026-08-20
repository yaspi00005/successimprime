#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige trois problemes signales sur le module Livraisons / Bons de
livraison :

1) "Jeton de securite invalide" sur /bons-livraison/{id}/livrer
   Cause reelle : la methode livrer() du controleur des bons de
   livraison etait un copier-coller de celle des lignes de commande
   (LivraisonController) -- elle attendait un identifiant de LIGNE,
   pas de BON, et verifiait donc un jeton CSRF different de celui
   genere par le bouton "Marquer comme livre" du bon. Corrige : la
   methode utilise maintenant BonLivraison::marquerLivre(), deja
   totalement implementee sur l'entite mais jamais appelee.

2) Page d'impression manquante (bons_livraison/print.html.twig).

3) Possibilite de demarrer toutes les livraisons d'une commande en un
   clic, et de faire des actions en masse sur une selection de
   lignes (cases a cocher + bouton "Demarrer la selection").

Executer depuis la racine du projet :
    python3 fix_livrer_bon_impression_actions_masse.py
"""

import os
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


def creer_fichier(chemin, contenu, label):
    if os.path.isfile(chemin):
        with open(chemin, "r", encoding="utf-8") as f:
            existant = f.read()
        if existant == contenu:
            print(f"[SKIP] {label} : deja applique.")
            return True
        print(
            f"[ERREUR] {label} : {chemin} existe deja avec un contenu "
            f"different. Rien n'a ete ecrase."
        )
        return False

    dossier = os.path.dirname(chemin)
    if dossier and not os.path.isdir(dossier):
        os.makedirs(dossier, exist_ok=True)

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)

    print(f"[OK] {label}")
    return True


resultats = []

resultats.append(appliquer(
    "src/Controller/BonLivraisonController.php",
"   #[Route(\n    '/{id}/livrer',\n    name: 'livrer',\n    requirements: [\n        'id' => '\\d+',\n    ],\n    methods: ['POST']\n)]\npublic function livrer(\n    CommandesDetails $detail,\n    Request $request,\n    EntityManagerInterface $em,\n    StockService $stockService\n): Response {\n    $this->verifierJeton(\n        $request,\n        'livraison_livrer_' . $detail->getId()\n    );\n\n    try {\n        /*\n         * ========================================================\n         * 1. LA LIGNE DOIT ÊTRE EN LIVRAISON\n         * ========================================================\n         */\n        if (\n            $detail->getStatutProduction()\n            !== CommandesDetails::PRODUCTION_EN_LIVRAISON\n        ) {\n            throw new \\LogicException(\n                'La ligne doit être en livraison avant d’être confirmée comme livrée.'\n            );\n        }\n\n\n        /*\n         * ========================================================\n         * 2. ARTICLE EN STOCK = LIVRAISON DIRECTE AUTORISÉE\n         * ========================================================\n         */\n        if (\n            $detail->getTypeLigne()\n            === CommandesDetails::TYPE_ARTICLE\n        ) {\n            $article =\n                $detail->getArticle();\n\n            if ($article === null) {\n                throw new \\LogicException(\n                    'Aucun article en stock n’est associé à cette ligne.'\n                );\n            }\n\n\n            /*\n             * Quantité réellement livrée.\n             *\n             * Pour cette route simple, on considère\n             * que toute la ligne est livrée.\n             *\n             * Les livraisons partielles restent gérées\n             * par le module Bon de Livraison.\n             */\n            $quantite =\n                (float) $detail->getQuantite();\n\n            if ($quantite <= 0) {\n                throw new \\LogicException(\n                    'La quantité à livrer est invalide.'\n                );\n            }\n\n\n            /*\n             * Référence unique de cette sortie.\n             *\n             * Cela permet aussi à StockService\n             * d’éviter une double consommation.\n             */\n            $reference =\n                sprintf(\n                    'LIV-DIRECT-%06d',\n                    (int) $detail->getId()\n                );\n\n\n            /*\n             * ====================================================\n             * SORTIE DU STOCK\n             * ====================================================\n             *\n             * calculerBesoinsDetail() sait maintenant\n             * que TYPE_ARTICLE consomme directement\n             * detail->article.\n             */\n            $stockService->consommerPourDetail(\n                $detail,\n                StockSorties::ORIGINE_LIVRAISON,\n                $reference,\n                $quantite\n            );\n\n\n            /*\n             * ====================================================\n             * STATUT LIVRÉ\n             * ====================================================\n             */\n            $detail->marquerLivree();\n\n\n            $em->flush();\n\n\n            $this->addFlash(\n                'success',\n                sprintf(\n                    'La livraison de « %s » a été confirmée. '\n                    . 'La sortie de stock a été enregistrée.',\n                    $detail->getDesignation()\n                )\n            );\n\n\n            return $this->redirectToRoute(\n                'app_livraisons_show',\n                [\n                    'id' => $detail->getId(),\n                ]\n            );\n        }\n\n\n        /*\n         * ========================================================\n         * 3. AUTRES LIGNES\n         * ========================================================\n         *\n         * Pour les produits provenant de la production,\n         * on garde le circuit Bon de Livraison.\n         */\n        throw new \\LogicException(\n            sprintf(\n                'La ligne « %s » doit être livrée à partir d’un bon de livraison.',\n                $detail->getDesignation()\n            )\n        );\n\n    } catch (\n        \\LogicException |\n        \\RuntimeException |\n        \\DomainException $e\n    ) {\n        $this->addFlash(\n            'error',\n            $e->getMessage()\n        );\n    }\n\n\n    return $this->redirectToRoute(\n        'app_livraisons_show',\n        [\n            'id' => $detail->getId(),\n        ]\n    );\n}\n\n",
"   #[Route(\n    '/{id}/livrer',\n    name: 'livrer',\n    requirements: [\n        'id' => '\\d+',\n    ],\n    methods: ['POST']\n)]\npublic function livrer(\n    BonLivraison $bon,\n    Request $request,\n    EntityManagerInterface $em\n): Response {\n    $utilisateur =\n        $this->utilisateurConnecte();\n\n    $this->verifierJeton(\n        $request,\n        'bon_livraison_livrer_' . $bon->getId()\n    );\n\n    try {\n        $bon->marquerLivre(\n            $utilisateur\n        );\n\n        $em->flush();\n\n        $this->addFlash(\n            'success',\n            sprintf(\n                'Le bon de livraison %s a été marqué comme livré.',\n                $bon->getNumero()\n            )\n        );\n    } catch (\n        \\LogicException |\n        \\InvalidArgumentException $e\n    ) {\n        $this->addFlash(\n            'error',\n            $e->getMessage()\n        );\n    }\n\n    return $this->redirectToRoute(\n        'app_bons_livraison_show',\n        [\n            'id' => $bon->getId(),\n        ]\n    );\n}\n\n",
    "1) BonLivraisonController : corrige livrer() (jeton CSRF invalide)",
))

resultats.append(creer_fichier(
    "templates/bons_livraison/print.html.twig",
'<!DOCTYPE html>\n<html lang="fr">\n\t<head>\n\t\t<meta charset="UTF-8">\n\t\t<meta name="viewport" content="width=device-width, initial-scale=1">\n\t\t<title>Bon de livraison {{ bon.numero }}</title>\n\t\t<style>\n\t\t\t@page {\n\t\t\t\tsize: A4;\n\t\t\t\tmargin: 15mm;\n\t\t\t}\n\t\t\t* {\n\t\t\t\tbox-sizing: border-box;\n\t\t\t}\n\t\t\thtml,\n\t\t\tbody {\n\t\t\t\tmargin: 0;\n\t\t\t\tpadding: 0;\n\t\t\t\tbackground: #eef0f4;\n\t\t\t\tcolor: #111;\n\t\t\t\tfont-family: Arial, Helvetica, sans-serif;\n\t\t\t}\n\t\t\t.print-toolbar {\n\t\t\t\tdisplay: flex;\n\t\t\t\tjustify-content: center;\n\t\t\t\tgap: 10px;\n\t\t\t\tpadding: 15px;\n\t\t\t}\n\t\t\t.print-toolbar button,\n\t\t\t.print-toolbar a {\n\t\t\t\tpadding: 10px 18px;\n\t\t\t\tborder: 0;\n\t\t\t\tborder-radius: 5px;\n\t\t\t\tcolor: #fff;\n\t\t\t\tbackground: #6259ca;\n\t\t\t\tfont-size: 14px;\n\t\t\t\ttext-decoration: none;\n\t\t\t\tcursor: pointer;\n\t\t\t}\n\t\t\t.print-toolbar a {\n\t\t\t\tbackground: #5b6470;\n\t\t\t}\n\t\t\t.sheet {\n\t\t\t\twidth: 190mm;\n\t\t\t\tmin-height: 260mm;\n\t\t\t\tmargin: 0 auto 20px;\n\t\t\t\tpadding: 10mm;\n\t\t\t\tbackground: #fff;\n\t\t\t}\n\t\t\t.header {\n\t\t\t\tdisplay: flex;\n\t\t\t\talign-items: flex-start;\n\t\t\t\tjustify-content: space-between;\n\t\t\t\tgap: 5mm;\n\t\t\t\tpadding-bottom: 4mm;\n\t\t\t\tborder-bottom: 1mm solid #111;\n\t\t\t}\n\t\t\t.company {\n\t\t\t\tfont-size: 20px;\n\t\t\t\tfont-weight: 800;\n\t\t\t\ttext-transform: uppercase;\n\t\t\t}\n\t\t\t.document-title {\n\t\t\t\tmargin-top: 1mm;\n\t\t\t\tfont-size: 13px;\n\t\t\t\tfont-weight: 700;\n\t\t\t\tletter-spacing: 1px;\n\t\t\t\ttext-transform: uppercase;\n\t\t\t}\n\t\t\t.bon-numero {\n\t\t\t\ttext-align: right;\n\t\t\t\tfont-size: 11px;\n\t\t\t}\n\t\t\t.bon-numero strong {\n\t\t\t\tdisplay: block;\n\t\t\t\tmargin-top: 1mm;\n\t\t\t\tfont-size: 16px;\n\t\t\t}\n\t\t\t.grid {\n\t\t\t\tdisplay: grid;\n\t\t\t\tgrid-template-columns: 1fr 1fr;\n\t\t\t\tgap: 4mm 8mm;\n\t\t\t\tmargin: 5mm 0;\n\t\t\t}\n\t\t\t.field-label {\n\t\t\t\tdisplay: block;\n\t\t\t\tmargin-bottom: 0.5mm;\n\t\t\t\tfont-size: 9px;\n\t\t\t\tfont-weight: 700;\n\t\t\t\tcolor: #555;\n\t\t\t\ttext-transform: uppercase;\n\t\t\t}\n\t\t\t.field-value {\n\t\t\t\tdisplay: block;\n\t\t\t\tfont-size: 12px;\n\t\t\t\tfont-weight: 700;\n\t\t\t\tline-height: 1.3;\n\t\t\t}\n\t\t\t.statut {\n\t\t\t\tdisplay: inline-block;\n\t\t\t\tmargin-top: 5mm;\n\t\t\t\tpadding: 1.5mm 4mm;\n\t\t\t\tborder-radius: 3mm;\n\t\t\t\tfont-size: 10px;\n\t\t\t\tfont-weight: 700;\n\t\t\t\ttext-transform: uppercase;\n\t\t\t\tbackground: #eee;\n\t\t\t}\n\t\t\ttable {\n\t\t\t\twidth: 100%;\n\t\t\t\tmargin-top: 5mm;\n\t\t\t\tborder-collapse: collapse;\n\t\t\t\tfont-size: 11px;\n\t\t\t}\n\t\t\tth,\n\t\t\ttd {\n\t\t\t\tpadding: 2.5mm;\n\t\t\t\tborder: 0.3mm solid #999;\n\t\t\t\ttext-align: left;\n\t\t\t}\n\t\t\tth {\n\t\t\t\tbackground: #f2f2f5;\n\t\t\t\tfont-size: 9px;\n\t\t\t\ttext-transform: uppercase;\n\t\t\t}\n\t\t\ttd.text-center,\n\t\t\tth.text-center {\n\t\t\t\ttext-align: center;\n\t\t\t}\n\t\t\t.observation {\n\t\t\t\tmargin-top: 5mm;\n\t\t\t\tpadding: 3mm;\n\t\t\t\tborder: 0.3mm dashed #999;\n\t\t\t\tfont-size: 11px;\n\t\t\t}\n\t\t\t.signatures {\n\t\t\t\tdisplay: grid;\n\t\t\t\tgrid-template-columns: 1fr 1fr;\n\t\t\t\tgap: 8mm;\n\t\t\t\tmargin-top: 12mm;\n\t\t\t}\n\t\t\t.signature-box {\n\t\t\t\tpadding-top: 2mm;\n\t\t\t\tborder-top: 0.3mm solid #111;\n\t\t\t\tfont-size: 10px;\n\t\t\t}\n\t\t\t.signature-box strong {\n\t\t\t\tdisplay: block;\n\t\t\t\tmargin-bottom: 12mm;\n\t\t\t\tfont-size: 11px;\n\t\t\t}\n\t\t\t.footer {\n\t\t\t\tdisplay: flex;\n\t\t\t\tjustify-content: space-between;\n\t\t\t\tgap: 4mm;\n\t\t\t\tmargin-top: 10mm;\n\t\t\t\tpadding-top: 3mm;\n\t\t\t\tborder-top: 0.3mm solid #999;\n\t\t\t\tfont-size: 8px;\n\t\t\t\tcolor: #666;\n\t\t\t}\n\t\t\t@media print {\n\t\t\t\thtml,\n\t\t\t\tbody {\n\t\t\t\t\tbackground: #fff;\n\t\t\t\t}\n\t\t\t\t.print-toolbar {\n\t\t\t\t\tdisplay: none !important;\n\t\t\t\t}\n\t\t\t\t.sheet {\n\t\t\t\t\twidth: auto;\n\t\t\t\t\tmin-height: 0;\n\t\t\t\t\tmargin: 0;\n\t\t\t\t\tpadding: 0;\n\t\t\t\t}\n\t\t\t}\n\t\t</style>\n\t</head>\n\t<body>\n\n\t\t{% set commande = bon.commande %}\n\t\t{% set client = commande ? commande.clients : null %}\n\n\t\t<div class="print-toolbar">\n\t\t\t<a href="{{ path(\'app_bons_livraison_show\', { id: bon.id }) }}">Retour au bon</a>\n\t\t\t<button type="button" onclick="window.print()">Imprimer</button>\n\t\t</div>\n\n\t\t<main class="sheet">\n\n\t\t\t<header class="header">\n\t\t\t\t<div>\n\t\t\t\t\t<div class="company">SUCCESS IMPRIM</div>\n\t\t\t\t\t<div class="document-title">Bon de livraison</div>\n\t\t\t\t</div>\n\t\t\t\t<div class="bon-numero">\n\t\t\t\t\tNuméro\n\t\t\t\t\t<strong>{{ bon.numero }}</strong>\n\t\t\t\t\t{{ bon.creeLe ? bon.creeLe|date(\'d/m/Y\') : \'—\' }}\n\t\t\t\t</div>\n\t\t\t</header>\n\n\t\t\t<div class="grid">\n\n\t\t\t\t<div>\n\t\t\t\t\t<span class="field-label">Commande</span>\n\t\t\t\t\t<span class="field-value">\n\t\t\t\t\t\t{% if commande %}\n\t\t\t\t\t\t\t{{ commande.numero|default(\'#\' ~ commande.id) }}\n\t\t\t\t\t\t{% else %}\n\t\t\t\t\t\t\t—\n\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t</span>\n\t\t\t\t</div>\n\n\t\t\t\t<div>\n\t\t\t\t\t<span class="field-label">Client</span>\n\t\t\t\t\t<span class="field-value">\n\t\t\t\t\t\t{{ client ? client.nomComplet : \'—\' }}\n\t\t\t\t\t</span>\n\t\t\t\t</div>\n\n\t\t\t\t<div>\n\t\t\t\t\t<span class="field-label">Réceptionnaire</span>\n\t\t\t\t\t<span class="field-value">\n\t\t\t\t\t\t{{ bon.nomReceptionnaire|default(client ? client.nomComplet : \'—\') }}\n\t\t\t\t\t</span>\n\t\t\t\t</div>\n\n\t\t\t\t<div>\n\t\t\t\t\t<span class="field-label">Téléphone</span>\n\t\t\t\t\t<span class="field-value">\n\t\t\t\t\t\t{{ bon.telephoneReceptionnaire|default(client ? client.telephone : \'—\') }}\n\t\t\t\t\t</span>\n\t\t\t\t</div>\n\n\t\t\t\t<div>\n\t\t\t\t\t<span class="field-label">Adresse de livraison</span>\n\t\t\t\t\t<span class="field-value">\n\t\t\t\t\t\t{{ bon.adresseLivraison|default(client ? client.adresse : \'—\') }}\n\t\t\t\t\t</span>\n\t\t\t\t</div>\n\n\t\t\t\t<div>\n\t\t\t\t\t<span class="field-label">Statut</span>\n\t\t\t\t\t<span class="field-value">\n\t\t\t\t\t\t<span class="statut">\n\t\t\t\t\t\t\t{% if bon.statut == \'brouillon\' %}\n\t\t\t\t\t\t\t\tBrouillon\n\t\t\t\t\t\t\t{% elseif bon.statut == \'valide\' %}\n\t\t\t\t\t\t\t\tValidé\n\t\t\t\t\t\t\t{% elseif bon.statut == \'livre\' %}\n\t\t\t\t\t\t\t\tLivré\n\t\t\t\t\t\t\t{% elseif bon.statut == \'annule\' %}\n\t\t\t\t\t\t\t\tAnnulé\n\t\t\t\t\t\t\t{% else %}\n\t\t\t\t\t\t\t\t{{ bon.statut|replace({\'_\': \' \'})|capitalize }}\n\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t</span>\n\t\t\t\t\t</span>\n\t\t\t\t</div>\n\n\t\t\t</div>\n\n\t\t\t<table>\n\t\t\t\t<thead>\n\t\t\t\t\t<tr>\n\t\t\t\t\t\t<th>#</th>\n\t\t\t\t\t\t<th>Désignation</th>\n\t\t\t\t\t\t<th class="text-center">Qté commandée</th>\n\t\t\t\t\t\t<th class="text-center">Qté livrée</th>\n\t\t\t\t\t</tr>\n\t\t\t\t</thead>\n\t\t\t\t<tbody>\n\t\t\t\t\t{% for ligne in bon.lignes %}\n\t\t\t\t\t\t<tr>\n\t\t\t\t\t\t\t<td class="text-center">{{ loop.index }}</td>\n\t\t\t\t\t\t\t<td>{{ ligne.designation }}</td>\n\t\t\t\t\t\t\t<td class="text-center">{{ ligne.quantiteCommandee }}</td>\n\t\t\t\t\t\t\t<td class="text-center">{{ ligne.quantiteLivree }}</td>\n\t\t\t\t\t\t</tr>\n\t\t\t\t\t{% else %}\n\t\t\t\t\t\t<tr>\n\t\t\t\t\t\t\t<td colspan="4" class="text-center">Aucune ligne.</td>\n\t\t\t\t\t\t</tr>\n\t\t\t\t\t{% endfor %}\n\t\t\t\t</tbody>\n\t\t\t</table>\n\n\t\t\t{% if bon.observation %}\n\t\t\t\t<div class="observation">\n\t\t\t\t\t<span class="field-label">Observation</span>\n\t\t\t\t\t{{ bon.observation|nl2br }}\n\t\t\t\t</div>\n\t\t\t{% endif %}\n\n\t\t\t<div class="signatures">\n\n\t\t\t\t<div class="signature-box">\n\t\t\t\t\t<strong>Livré par</strong>\n\t\t\t\t\t{{ bon.livrePar ? bon.livrePar.username : (bon.creePar ? bon.creePar.username : \'—\') }}\n\t\t\t\t</div>\n\n\t\t\t\t<div class="signature-box">\n\t\t\t\t\t<strong>Reçu par (signature)</strong>\n\t\t\t\t\t{{ bon.nomReceptionnaire|default(\'—\') }}\n\t\t\t\t</div>\n\n\t\t\t</div>\n\n\t\t\t<footer class="footer">\n\t\t\t\t<span>Créé le {{ bon.creeLe ? bon.creeLe|date(\'d/m/Y H:i\') : \'—\' }} par {{ bon.creePar ? bon.creePar.username : \'—\' }}</span>\n\t\t\t\t<span>Validé le {{ bon.valideLe ? bon.valideLe|date(\'d/m/Y H:i\') : \'—\' }}</span>\n\t\t\t\t<span>Livré le {{ bon.livreLe ? bon.livreLe|date(\'d/m/Y H:i\') : \'—\' }}</span>\n\t\t\t</footer>\n\n\t\t</main>\n\n\t\t<script>\n\t\t\tif (new URLSearchParams(window.location.search).get(\'autoPrint\') === \'1\') {\nwindow.addEventListener(\'load\', function () {\nwindow.print();\n});\n}\n\t\t</script>\n\t</body>\n</html>\n',
    "2) Cree templates/bons_livraison/print.html.twig (page manquante)",
))

resultats.append(appliquer(
    "src/Controller/LivraisonController.php",
"        return $this->redirectToRoute(\n            'app_livraisons_show',\n            [\n                'id' => $detail->getId(),\n            ]\n        );\n    }\n\n    /*\n     * ============================================================\n     * MARQUER COMME LIVRÉE",
'        return $this->redirectToRoute(\n            \'app_livraisons_show\',\n            [\n                \'id\' => $detail->getId(),\n            ]\n        );\n    }\n\n    /*\n     * ============================================================\n     * DÉMARRER PLUSIEURS LIGNES D\'UNE COMMANDE EN UNE FOIS\n     * ============================================================\n     *\n     * Un seul formulaire/route pour deux usages :\n     * - "Démarrer toutes les livraisons" (champ caché tout=1) ;\n     * - "Démarrer la sélection" (cases à cocher lignes[]).\n     * ============================================================\n     */\n    #[Route(\n        \'/commande/{id}/demarrer-masse\',\n        name: \'demarrer_masse\',\n        requirements: [\n            \'id\' => \'\\d+\',\n        ],\n        methods: [\'POST\']\n    )]\n    public function demarrerMasse(\n        Commandes $commande,\n        Request $request,\n        CommandesDetailsRepository $commandesDetailsRepository,\n        EntityManagerInterface $em\n    ): Response {\n        $this->verifierJeton(\n            $request,\n            \'livraison_demarrer_masse_\' . $commande->getId()\n        );\n\n        $qb = $commandesDetailsRepository\n            ->createQueryBuilder(\'detail\')\n            ->andWhere(\'detail.commande = :commande\')\n            ->andWhere(\'detail.statutProduction = :statut\')\n            ->setParameter(\'commande\', $commande)\n            ->setParameter(\n                \'statut\',\n                CommandesDetails::PRODUCTION_PRETE_LIVRAISON\n            );\n\n        if (!$request->request->getBoolean(\'tout\')) {\n            $ids = array_map(\n                \'intval\',\n                $request->request->all(\'lignes\')\n            );\n\n            if ($ids === []) {\n                $this->addFlash(\n                    \'error\',\n                    \'Aucune ligne sélectionnée.\'\n                );\n\n                return $this->redirectToRoute(\n                    \'app_livraisons_commande\',\n                    [\n                        \'id\' => $commande->getId(),\n                    ]\n                );\n            }\n\n            $qb\n                ->andWhere(\'detail.id IN (:ids)\')\n                ->setParameter(\'ids\', $ids);\n        }\n\n        $lignes = $qb->getQuery()->getResult();\n\n        $nombreDemarrees = 0;\n\n        foreach ($lignes as $detail) {\n            try {\n                $detail->marquerEnLivraison();\n\n                ++$nombreDemarrees;\n            } catch (\\LogicException) {\n                continue;\n            }\n        }\n\n        if ($nombreDemarrees > 0) {\n            $em->flush();\n\n            $this->addFlash(\n                \'success\',\n                sprintf(\n                    \'%d livraison(s) démarrée(s).\',\n                    $nombreDemarrees\n                )\n            );\n        } else {\n            $this->addFlash(\n                \'error\',\n                \'Aucune ligne n’a pu être démarrée.\'\n            );\n        }\n\n        return $this->redirectToRoute(\n            \'app_livraisons_commande\',\n            [\n                \'id\' => $commande->getId(),\n            ]\n        );\n    }\n\n    /*\n     * ============================================================\n     * MARQUER COMME LIVRÉE',
    "3) LivraisonController : nouvelle action demarrerMasse()",
))

resultats.append(appliquer(
    "templates/livraisons/show_commande.html.twig",
'\t\t<div class="card mb-3">\n\n\t\t\t<div class="card-header">\n\t\t\t\t<h3 class="card-title mb-0">\n\t\t\t\t\t<i class="fa fa-list mr-1"></i>\n\t\t\t\t\tLignes à livrer\n\t\t\t\t</h3>\n\t\t\t</div>\n\n\t\t\t{% if lignes|length == 0 %}\n\n\t\t\t\t<div class="card-body text-center text-muted py-4">\n\t\t\t\t\tAucune ligne à livrer pour cette commande.\n\t\t\t\t</div>\n\n\t\t\t{% else %}\n\n\t\t\t\t<div class="table-responsive">\n\n\t\t\t\t\t<table class="table table-bordered table-hover mb-0">\n\n\t\t\t\t\t\t<thead>\n\n\t\t\t\t\t\t\t<tr>\n\t\t\t\t\t\t\t\t<th>Produit / Désignation</th>\n\t\t\t\t\t\t\t\t<th class="text-center">Quantité</th>\n',
'\t\t{% set nbPretes = lignes|filter(l => l.statutProduction == \'prete_livraison\')|length %}\n\n\t\t<form id="formDemarrerMasse" method="post" action="{{ path( \'app_livraisons_demarrer_masse\', { id: commande.id } ) }}">\n\t\t\t<input type="hidden" name="_token" value="{{ csrf_token( \'livraison_demarrer_masse_\' ~ commande.id ) }}">\n\t\t</form>\n\n\t\t<div class="card mb-3">\n\n\t\t\t<div class="card-header d-flex justify-content-between align-items-center flex-wrap">\n\n\t\t\t\t<h3 class="card-title mb-0">\n\t\t\t\t\t<i class="fa fa-list mr-1"></i>\n\t\t\t\t\tLignes à livrer\n\t\t\t\t</h3>\n\n\t\t\t\t{% if nbPretes > 0 %}\n\n\t\t\t\t\t<div class="btn-group">\n\n\t\t\t\t\t\t<button type="submit" name="tout" value="1" form="formDemarrerMasse" class="btn btn-sm btn-warning" onclick="return confirm(\'Démarrer les {{ nbPretes }} livraison(s) prête(s) ?\');">\n\t\t\t\t\t\t\t<i class="fa fa-truck mr-1"></i>\n\t\t\t\t\t\t\tDémarrer toutes les livraisons ({{ nbPretes }})\n\t\t\t\t\t\t</button>\n\n\t\t\t\t\t\t<button type="submit" form="formDemarrerMasse" class="btn btn-sm btn-primary" onclick="return confirm(\'Démarrer la livraison des lignes sélectionnées ?\');">\n\t\t\t\t\t\t\t<i class="fa fa-check-square-o mr-1"></i>\n\t\t\t\t\t\t\tDémarrer la sélection\n\t\t\t\t\t\t</button>\n\n\t\t\t\t\t</div>\n\n\t\t\t\t{% endif %}\n\n\t\t\t</div>\n\n\t\t\t{% if lignes|length == 0 %}\n\n\t\t\t\t<div class="card-body text-center text-muted py-4">\n\t\t\t\t\tAucune ligne à livrer pour cette commande.\n\t\t\t\t</div>\n\n\t\t\t{% else %}\n\n\t\t\t\t<div class="table-responsive">\n\n\t\t\t\t\t<table class="table table-bordered table-hover mb-0">\n\n\t\t\t\t\t\t<thead>\n\n\t\t\t\t\t\t\t<tr>\n\t\t\t\t\t\t\t\t<th class="text-center">\n\t\t\t\t\t\t\t\t\t{% if nbPretes > 0 %}\n\t\t\t\t\t\t\t\t\t\t<input type="checkbox" id="js-tout-selectionner" title="Tout sélectionner">\n\t\t\t\t\t\t\t\t\t{% endif %}\n\t\t\t\t\t\t\t\t</th>\n\t\t\t\t\t\t\t\t<th>Produit / Désignation</th>\n\t\t\t\t\t\t\t\t<th class="text-center">Quantité</th>\n',
    "4) show_commande.html.twig : boutons demarrer tout / selection",
))

resultats.append(appliquer(
    "templates/livraisons/show_commande.html.twig",
'\t\t\t\t\t\t{% for detail in lignes %}\n\n\t\t\t\t\t\t\t\t<tr>\n\n\t\t\t\t\t\t\t\t\t{# PRODUIT #}\n\t\t\t\t\t\t\t\t\t<td class="align-middle">\n\n\t\t\t\t\t\t\t\t\t\t<strong>\n\t\t\t\t\t\t\t\t\t\t\t{{ detail.designation }}\n\t\t\t\t\t\t\t\t\t\t</strong>\n',
'\t\t\t\t\t\t{% for detail in lignes %}\n\n\t\t\t\t\t\t\t\t<tr>\n\n\t\t\t\t\t\t\t\t\t{# SÉLECTION #}\n\t\t\t\t\t\t\t\t\t<td class="text-center align-middle">\n\n\t\t\t\t\t\t\t\t\t\t{% if detail.statutProduction == \'prete_livraison\' %}\n\t\t\t\t\t\t\t\t\t\t\t<input type="checkbox" name="lignes[]" value="{{ detail.id }}" form="formDemarrerMasse" class="js-ligne-a-demarrer">\n\t\t\t\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t\t\t\t</td>\n\n\n\t\t\t\t\t\t\t\t\t{# PRODUIT #}\n\t\t\t\t\t\t\t\t\t<td class="align-middle">\n\n\t\t\t\t\t\t\t\t\t\t<strong>\n\t\t\t\t\t\t\t\t\t\t\t{{ detail.designation }}\n\t\t\t\t\t\t\t\t\t\t</strong>\n',
    "5) show_commande.html.twig : case a cocher par ligne",
))

resultats.append(appliquer(
    "templates/livraisons/show_commande.html.twig",
"\t\tdocument.addEventListener('DOMContentLoaded', function () {\n\ndocument.querySelectorAll('.js-confirmer-livraison').forEach(function (formulaire) {\n",
"\t\tdocument.addEventListener('DOMContentLoaded', function () {\n\nconst toutSelectionner = document.getElementById('js-tout-selectionner');\n\nif (toutSelectionner) {\ntoutSelectionner.addEventListener('change', function () {\ndocument.querySelectorAll('.js-ligne-a-demarrer').forEach(function (case_) {\ncase_.checked = toutSelectionner.checked;\n});\n});\n}\n\ndocument.querySelectorAll('.js-confirmer-livraison').forEach(function (formulaire) {\n",
    "6) show_commande.html.twig : JS tout selectionner",
))


echecs = resultats.count(False)

print()
if echecs:
    print(f"Termine avec {echecs} erreur(s). Voir les [ERREUR] ci-dessus.")
    sys.exit(1)
else:
    print("Termine sans erreur.")
