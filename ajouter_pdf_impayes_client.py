#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute un bouton "PDF des impayes" sur la fiche client : genere un
PDF listant toutes les commandes non entierement payees du client
(deja paye, reste a payer, detail des lignes de chaque commande).

Reutilise exactement le meme moteur PDF (dompdf) et le meme calcul
du reste a payer (a partir des paiements VALIDES, jamais du champ
fige montantApayer) que la page fiche client existante.

Fichiers concernes :
  - src/Controller/ClientsController.php (nouvelle route + PDF)
  - templates/clients/show.html.twig (bouton)
  - templates/clients/pdf_impayes.html.twig (nouveau)

Usage:
    python3 ajouter_pdf_impayes_client.py /chemin/vers/successImprim
"""

import os
import subprocess
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


def lire(chemin):
    with open(chemin, "r", encoding="utf-8") as f:
        return f.read()


def ecrire(chemin, contenu):
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        f.write(contenu)
        f.flush()
        os.fsync(f.fileno())

    with open(chemin, "r", encoding="utf-8", newline="") as f:
        relu = f.read()

    return relu == contenu


def appliquer_paires(racine, chemin_relatif, paires):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    contenu = lire(chemin_absolu)
    contenu_original = contenu
    tout_ok = True

    for ancien, nouveau, description in paires:
        if nouveau in contenu:
            print("  [SKIP] " + description + " (deja applique)")
            continue

        if ancien not in contenu:
            print("  [ECHEC] " + description + " : bloc de reference introuvable.")
            tout_ok = False
            continue

        if contenu.count(ancien) > 1:
            print("  [ECHEC] " + description + " : bloc de reference trouve plusieurs fois, abandon.")
            tout_ok = False
            continue

        contenu = contenu.replace(ancien, nouveau, 1)
        print("  [OK] " + description)

    if contenu == contenu_original:
        return tout_ok

    if not ecrire(chemin_absolu, contenu):
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return tout_ok


def creer_template(racine):
    chemin_relatif = "templates/clients/pdf_impayes.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if os.path.isfile(chemin_absolu):
        if lire(chemin_absolu) == NOUVEAU_TEMPLATE:
            print("[SKIP] " + chemin_relatif + " (deja applique)")
            return True
        print("[ATTENTION] " + chemin_relatif + " existe deja avec un contenu different -> non ecrase.")
        return False

    dossier_parent = os.path.dirname(chemin_absolu)
    if not os.path.isdir(dossier_parent):
        os.makedirs(dossier_parent, exist_ok=True)

    if not ecrire(chemin_absolu, NOUVEAU_TEMPLATE):
        print("[ECHEC VERIFICATION] " + chemin_relatif + " : le contenu relu ne correspond pas.")
        return False

    print("[OK VERIFIE] " + chemin_relatif + " (nouveau fichier)")
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))
    return True


CTRL_PAIRES = [
    (
        'use Symfony\\Bridge\\Doctrine\\Attribute\\MapEntity;\nuse Doctrine\\DBAL\\Exception\\UniqueConstraintViolationException;\n',
        'use Symfony\\Bridge\\Doctrine\\Attribute\\MapEntity;\nuse Doctrine\\DBAL\\Exception\\UniqueConstraintViolationException;\nuse Dompdf\\Dompdf;\nuse Dompdf\\Options;\n',
        "import Dompdf/Options"
    ),
    (
        "    #[Route(\n        '/{id}',\n        name: 'app_clients_delete',\n",
        '    #[Route(\n        \'/fiche/{publicId}/impayes.pdf\',\n        name: \'app_clients_pdf_impayes\',\n        methods: [\'GET\']\n    )]\n    public function pdfImpayes(\n        #[MapEntity(mapping: [\n            \'publicId\' => \'publicId\',\n        ])]\n        Clients $client,\n        CommandesRepository $commandesRepository\n    ): Response {\n        $commandes = $commandesRepository->findBy(\n            [\n                \'clients\' => $client,\n                \'deleted\' => false,\n            ],\n            [\n                \'dateCommande\' => \'DESC\',\n            ]\n        );\n\n        /*\n         * Même calcul que ClientsController::show() : le\n         * statut réel du paiement se calcule à partir des\n         * paiements validés, jamais depuis un champ figé\n         * (montantApayer/statutPaiement en base ne sont pas\n         * fiables, voir CommandesRepository).\n         */\n        $commandesImpayees = [];\n        $totalCommandes = 0;\n        $totalPaye = 0;\n        $totalReste = 0;\n\n        foreach ($commandes as $commande) {\n            $montantCommande = (int) $commande->getTotalTtc();\n            $totalPayeCommande = 0;\n\n            foreach ($commande->getPaiements() as $paiement) {\n                if ($paiement->getStatut() !== Paiements::STATUT_VALIDE) {\n                    continue;\n                }\n\n                $totalPayeCommande += (int) $paiement->getMontant();\n            }\n\n            $resteCommande = max(0, $montantCommande - $totalPayeCommande);\n\n            if ($resteCommande <= 0) {\n                continue;\n            }\n\n            $commandesImpayees[] = [\n                \'commande\' => $commande,\n                \'totalTtc\' => $montantCommande,\n                \'totalPaye\' => $totalPayeCommande,\n                \'resteAPayer\' => $resteCommande,\n            ];\n\n            $totalCommandes += $montantCommande;\n            $totalPaye += $totalPayeCommande;\n            $totalReste += $resteCommande;\n        }\n\n        $projectDir = $this->getParameter(\'kernel.project_dir\');\n\n        $html = $this->renderView(\n            \'clients/pdf_impayes.html.twig\',\n            [\n                \'client\' => $client,\n                \'commandes\' => $commandesImpayees,\n                \'totalCommandes\' => $totalCommandes,\n                \'totalPaye\' => $totalPaye,\n                \'totalReste\' => $totalReste,\n                \'genereLe\' => new \\DateTimeImmutable(),\n                \'logo\' => $this->imageVersDataUri(\n                    $projectDir . \'/public/assets/images/brand/logo2.png\'\n                ),\n            ]\n        );\n\n        $options = new Options();\n        $options->set(\'defaultFont\', \'DejaVu Sans\');\n        $options->set(\'isRemoteEnabled\', true);\n        $options->set(\'isHtml5ParserEnabled\', true);\n\n        $dompdf = new Dompdf($options);\n        $dompdf->loadHtml($html, \'UTF-8\');\n        $dompdf->setPaper(\'A4\', \'portrait\');\n        $dompdf->render();\n\n        $contenuPdf = $dompdf->output();\n\n        return new Response(\n            $contenuPdf,\n            Response::HTTP_OK,\n            [\n                \'Content-Type\' => \'application/pdf\',\n                \'Content-Disposition\' => sprintf(\n                    \'inline; filename="impayes-%s.pdf"\',\n                    preg_replace(\'/[^A-Za-z0-9_-]/\', \'-\', $client->getNomComplet())\n                ),\n                \'Content-Length\' => (string) strlen($contenuPdf),\n            ]\n        );\n    }\n\n    private function imageVersDataUri(string $chemin): ?string\n    {\n        if (!is_file($chemin) || !is_readable($chemin)) {\n            return null;\n        }\n\n        $contenu = file_get_contents($chemin);\n\n        if ($contenu === false) {\n            return null;\n        }\n\n        $mime = mime_content_type($chemin);\n\n        if (!$mime) {\n            $mime = \'image/png\';\n        }\n\n        return sprintf(\n            \'data:%s;base64,%s\',\n            $mime,\n            base64_encode($contenu)\n        );\n    }\n\n    #[Route(\n        \'/{id}\',\n        name: \'app_clients_delete\',\n',
        "route pdfImpayes() + helper imageVersDataUri()"
    ),
]

SHOW_PAIRES = [
    (
        '<a href="{{ path(\'app_clients_index\') }}" class="btn btn-light">\n\t\t\t\t\t<i class="fa fa-arrow-left mr-1"></i>\n\t\t\t\t\tRetour\n\t\t\t\t</a>',
        '<a href="{{ path(\'app_clients_pdf_impayes\', { publicId: client.publicId }) }}" class="btn btn-danger" target="_blank">\n\t\t\t\t\t<i class="fa fa-file-pdf-o mr-1"></i>\n\t\t\t\t\tPDF des impayés\n\t\t\t\t</a>\n\n\t\t\t\t<a href="{{ path(\'app_clients_index\') }}" class="btn btn-light">\n\t\t\t\t\t<i class="fa fa-arrow-left mr-1"></i>\n\t\t\t\t\tRetour\n\t\t\t\t</a>',
        "bouton PDF des impayes"
    ),
]

NOUVEAU_TEMPLATE = '<!DOCTYPE html>\n\n<html lang="fr">\n\n\t<head>\n\n\t\t<meta charset="UTF-8">\n\n\t\t<title>\n\t\t\tRelevé des impayés - {{ client.nomComplet }}\n\t\t</title>\n\n\t\t<style>\n\n\t\t\t@page {\n\t\t\t\tmargin: 18mm 15mm;\n\t\t\t}\n\n\t\t\t* {\n\t\t\t\tbox-sizing: border-box;\n\t\t\t}\n\n\t\t\tbody {\n\t\t\t\tmargin: 0;\n\n\t\t\t\tfont-family: DejaVu Sans, sans-serif;\n\n\t\t\t\tfont-size: 10px;\n\t\t\t\tline-height: 1.4;\n\n\t\t\t\tcolor: #202938;\n\t\t\t}\n\n\t\t\t.header-table {\n\t\t\t\twidth: 100%;\n\t\t\t\tborder-collapse: collapse;\n\n\t\t\t\tmargin-bottom: 16px;\n\t\t\t}\n\n\t\t\t.header-left {\n\t\t\t\twidth: 55%;\n\t\t\t\tvertical-align: top;\n\t\t\t}\n\n\t\t\t.header-right {\n\t\t\t\twidth: 45%;\n\t\t\t\tvertical-align: top;\n\t\t\t\ttext-align: right;\n\t\t\t}\n\n\t\t\t.logo {\n\t\t\t\tmax-width: 90px;\n\t\t\t\tmax-height: 60px;\n\t\t\t}\n\n\t\t\t.company-name {\n\t\t\t\tmargin-top: 4px;\n\n\t\t\t\tfont-size: 16px;\n\t\t\t\tfont-weight: bold;\n\n\t\t\t\tcolor: #12346b;\n\t\t\t}\n\n\t\t\t.document-title {\n\t\t\t\tmargin-top: 6px;\n\n\t\t\t\tfont-size: 14px;\n\t\t\t\tfont-weight: bold;\n\n\t\t\t\ttext-transform: uppercase;\n\t\t\t}\n\n\t\t\t.date-generation {\n\t\t\t\tmargin-top: 4px;\n\n\t\t\t\tcolor: #6c757d;\n\t\t\t}\n\n\t\t\t.client-box {\n\t\t\t\tmargin-bottom: 16px;\n\n\t\t\t\tpadding: 10px 14px;\n\n\t\t\t\tborder: 1px solid #dfe3e8;\n\t\t\t\tborder-radius: 4px;\n\n\t\t\t\tbackground: #f8f9fb;\n\t\t\t}\n\n\t\t\t.client-box .nom {\n\t\t\t\tfont-size: 13px;\n\t\t\t\tfont-weight: bold;\n\t\t\t}\n\n\t\t\ttable.commandes {\n\t\t\t\twidth: 100%;\n\t\t\t\tborder-collapse: collapse;\n\n\t\t\t\tmargin-bottom: 4px;\n\t\t\t}\n\n\t\t\ttable.commandes th {\n\t\t\t\tbackground: #12346b;\n\t\t\t\tcolor: #fff;\n\n\t\t\t\tpadding: 6px 8px;\n\n\t\t\t\ttext-align: left;\n\n\t\t\t\tfont-size: 9px;\n\t\t\t\ttext-transform: uppercase;\n\t\t\t}\n\n\t\t\ttable.commandes td {\n\t\t\t\tpadding: 6px 8px;\n\n\t\t\t\tborder-bottom: 1px solid #e5e7eb;\n\n\t\t\t\tvertical-align: top;\n\t\t\t}\n\n\t\t\ttable.commandes tr.ligne-detail td {\n\t\t\t\tpadding-left: 20px;\n\n\t\t\t\tcolor: #4b5563;\n\t\t\t\tfont-size: 9px;\n\n\t\t\t\tborder-bottom: none;\n\t\t\t}\n\n\t\t\ttable.commandes tr.commande-header td {\n\t\t\t\tbackground: #f1f4f8;\n\t\t\t\tfont-weight: bold;\n\t\t\t}\n\n\t\t\t.text-right {\n\t\t\t\ttext-align: right;\n\t\t\t}\n\n\t\t\t.totaux {\n\t\t\t\twidth: 45%;\n\t\t\t\tmargin-left: auto;\n\n\t\t\t\tmargin-top: 16px;\n\n\t\t\t\tborder-collapse: collapse;\n\t\t\t}\n\n\t\t\t.totaux td {\n\t\t\t\tpadding: 6px 8px;\n\n\t\t\t\tborder-bottom: 1px solid #e5e7eb;\n\t\t\t}\n\n\t\t\t.totaux tr.total-reste td {\n\t\t\t\tfont-weight: bold;\n\t\t\t\tfont-size: 12px;\n\n\t\t\t\tcolor: #b42318;\n\n\t\t\t\tborder-top: 2px solid #12346b;\n\t\t\t\tborder-bottom: none;\n\t\t\t}\n\n\t\t\t.aucune-commande {\n\t\t\t\tpadding: 20px;\n\n\t\t\t\ttext-align: center;\n\n\t\t\t\tcolor: #6c757d;\n\n\t\t\t\tborder: 1px dashed #dfe3e8;\n\t\t\t\tborder-radius: 4px;\n\t\t\t}\n\n\t\t</style>\n\n\t</head>\n\n\t<body>\n\n\t\t<table class="header-table">\n\t\t\t<tr>\n\t\t\t\t<td class="header-left">\n\t\t\t\t\t{% if logo %}\n\t\t\t\t\t\t<img src="{{ logo }}" class="logo" alt="MDG Group">\n\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t<div class="company-name">MDG Group</div>\n\t\t\t\t</td>\n\n\t\t\t\t<td class="header-right">\n\t\t\t\t\t<div class="document-title">Relevé des impayés</div>\n\t\t\t\t\t<div class="date-generation">Édité le {{ genereLe|date(\'d/m/Y à H:i\') }}</div>\n\t\t\t\t</td>\n\t\t\t</tr>\n\t\t</table>\n\n\t\t<div class="client-box">\n\t\t\t<div class="nom">{{ client.nomComplet }}</div>\n\n\t\t\t{% if client.telephone %}\n\t\t\t\t<div>Tél : {{ client.telephone }}</div>\n\t\t\t{% endif %}\n\n\t\t\t{% if client.adresse %}\n\t\t\t\t<div>{{ client.adresse }}</div>\n\t\t\t{% endif %}\n\t\t</div>\n\n\t\t{% if commandes is empty %}\n\n\t\t\t<div class="aucune-commande">\n\t\t\t\tCe client n\'a aucune commande impayée ou partiellement payée à ce jour.\n\t\t\t</div>\n\n\t\t{% else %}\n\n\t\t\t<table class="commandes">\n\t\t\t\t<thead>\n\t\t\t\t\t<tr>\n\t\t\t\t\t\t<th>Commande</th>\n\t\t\t\t\t\t<th>Date</th>\n\t\t\t\t\t\t<th class="text-right">Total TTC</th>\n\t\t\t\t\t\t<th class="text-right">Payé</th>\n\t\t\t\t\t\t<th class="text-right">Reste à payer</th>\n\t\t\t\t\t</tr>\n\t\t\t\t</thead>\n\n\t\t\t\t<tbody>\n\t\t\t\t\t{% for ligne in commandes %}\n\n\t\t\t\t\t\t<tr class="commande-header">\n\t\t\t\t\t\t\t<td>{{ ligne.commande.numero }}</td>\n\t\t\t\t\t\t\t<td>{{ ligne.commande.dateCommande ? ligne.commande.dateCommande|date(\'d/m/Y\') : \'—\' }}</td>\n\t\t\t\t\t\t\t<td class="text-right">{{ ligne.totalTtc|number_format(0, \',\', \' \') }} FCFA</td>\n\t\t\t\t\t\t\t<td class="text-right">{{ ligne.totalPaye|number_format(0, \',\', \' \') }} FCFA</td>\n\t\t\t\t\t\t\t<td class="text-right">{{ ligne.resteAPayer|number_format(0, \',\', \' \') }} FCFA</td>\n\t\t\t\t\t\t</tr>\n\n\t\t\t\t\t\t{% for detail in ligne.commande.commandesDetails %}\n\t\t\t\t\t\t\t<tr class="ligne-detail">\n\t\t\t\t\t\t\t\t<td colspan="3">\n\t\t\t\t\t\t\t\t\t{{ detail.produit ? detail.produit.nom : detail.designation|default(\'Article\') }}\n\t\t\t\t\t\t\t\t</td>\n\t\t\t\t\t\t\t\t<td class="text-right">Qté : {{ detail.quantite }}</td>\n\t\t\t\t\t\t\t\t<td class="text-right">{{ detail.totalTtc|number_format(0, \',\', \' \') }} FCFA</td>\n\t\t\t\t\t\t\t</tr>\n\t\t\t\t\t\t{% endfor %}\n\n\t\t\t\t\t{% endfor %}\n\t\t\t\t</tbody>\n\t\t\t</table>\n\n\t\t\t<table class="totaux">\n\t\t\t\t<tr>\n\t\t\t\t\t<td>Total des commandes impayées</td>\n\t\t\t\t\t<td class="text-right">{{ totalCommandes|number_format(0, \',\', \' \') }} FCFA</td>\n\t\t\t\t</tr>\n\n\t\t\t\t<tr>\n\t\t\t\t\t<td>Déjà payé</td>\n\t\t\t\t\t<td class="text-right">{{ totalPaye|number_format(0, \',\', \' \') }} FCFA</td>\n\t\t\t\t</tr>\n\n\t\t\t\t<tr class="total-reste">\n\t\t\t\t\t<td>Reste à payer</td>\n\t\t\t\t\t<td class="text-right">{{ totalReste|number_format(0, \',\', \' \') }} FCFA</td>\n\t\t\t\t</tr>\n\t\t\t</table>\n\n\t\t{% endif %}\n\n\t</body>\n\n</html>\n'


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = []

    print("-" * 70)
    print("src/Controller/ClientsController.php")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "src/Controller/ClientsController.php", CTRL_PAIRES))
    print()

    print("-" * 70)
    print("templates/clients/show.html.twig")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "templates/clients/show.html.twig", SHOW_PAIRES))
    print()

    print("-" * 70)
    print("templates/clients/pdf_impayes.html.twig (nouveau)")
    print("-" * 70)
    resultats.append(creer_template(racine))
    print()

    chemin_controller = os.path.join(racine, "src/Controller/ClientsController.php")
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_controller],
            capture_output=True, text=True, timeout=30
        )
        print("php -l ClientsController.php : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place.")
        print()
        print("Sur la fiche d'un client, un bouton rouge 'PDF des impayes'")
        print("genere desormais un PDF listant ses commandes non entierement")
        print("payees, avec le detail de chaque commande, le total deja paye")
        print("et le reste a payer.")
    else:
        print("Un ou plusieurs blocs n'ont pas pu etre modifies (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()