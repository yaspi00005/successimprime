#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ajoute un "dossier partage" de secours pour les gros fichiers dont
l'envoi echoue depuis la fiche d'une commande.

Principe :
  1. Un dossier var/uploads/dossier_partage est cree. Il doit etre
     partage sur le reseau (proprietes -> partage) pour que les
     postes puissent y deposer des fichiers.
  2. Chaque travail d'une commande affiche desormais un numero de
     reference (Ref: #123) a cote de "Travail n(deg)...".
  3. Pour importer un fichier depose dans ce dossier, il doit etre
     renomme pour commencer par ce numero suivi d'un tiret ou d'un
     underscore (exemple : 123_logo-client.pdf).
  4. Une page Parametres > Dossier partage liste les fichiers en
     attente et un bouton "Lancer l'import" les rattache au bon
     travail, comme s'ils avaient ete envoyes normalement (le
     fichier est deplace, pas recopie : instantane meme pour un
     fichier de plusieurs Go).

Fichiers concernes par ce script :
  - src/Controller/FichierUploadController.php (nouvelles routes)
  - templates/commandes/show.html.twig (numero de reference affiche)
  - templates/base.html.twig (lien de menu)
  - templates/commande_fichiers/dossier_partage.html.twig (nouveau)

Usage:
    python3 ajouter_import_dossier_partage.py /chemin/vers/successImprim
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
    """
    paires : liste de tuples (ancien, nouveau, description).
    Applique chaque paire independamment : [OK] si appliquee,
    [SKIP] si deja presente, [ECHEC] si le bloc de reference est
    introuvable. Retourne True si le fichier est dans l'etat
    attendu au final (tout applique ou deja applique), False sinon.
    """
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
            print("  [ECHEC] " + description + " : bloc de reference trouve plusieurs fois, abandon par prudence.")
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


CTRL_PAIRES = [
    (
        'use App\\Entity\\CommandeDetailFichier;\nuse App\\Repository\\CommandeDetailFichierRepository;\nuse Doctrine\\ORM\\EntityManagerInterface;\n',
        'use App\\Entity\\CommandeDetailFichier;\nuse App\\Repository\\CommandeDetailFichierRepository;\nuse App\\Repository\\CommandesDetailsRepository;\nuse Doctrine\\ORM\\EntityManagerInterface;\n',
        "import CommandesDetailsRepository"
    ),
    (
        "    private string $dossierTemporaire;\n    private string $dossierFinal;\n\n    public function __construct(\n        KernelInterface $kernel\n    ) {\n        $this->dossierTemporaire =\n            $kernel->getProjectDir().'/var/uploads/commande_tmp';\n\n        $this->dossierFinal =\n            $kernel->getProjectDir().'/var/uploads/commandes';\n\n        foreach ([\n            $this->dossierTemporaire,\n            $this->dossierFinal,\n        ] as $dossier) {\n",
        "    private string $dossierTemporaire;\n    private string $dossierFinal;\n    private string $dossierPartage;\n\n    public function __construct(\n        KernelInterface $kernel\n    ) {\n        $this->dossierTemporaire =\n            $kernel->getProjectDir().'/var/uploads/commande_tmp';\n\n        $this->dossierFinal =\n            $kernel->getProjectDir().'/var/uploads/commandes';\n\n        $this->dossierPartage =\n            $kernel->getProjectDir().'/var/uploads/dossier_partage';\n\n        foreach ([\n            $this->dossierTemporaire,\n            $this->dossierFinal,\n            $this->dossierPartage,\n        ] as $dossier) {\n",
        "propriete + creation dossier_partage"
    ),
    (
        '    private function assemblerFichier(\n',
        "    #[Route(\n        '/dossier-partage',\n        name: 'app_fichier_dossier_partage',\n        methods: ['GET']\n    )]\n    public function dossierPartage(): Response\n    {\n        $this->denyAccessUnlessGranted('ROLE_ADMIN');\n\n        $fichiers = [];\n\n        foreach (glob($this->dossierPartage.'/*') ?: [] as $chemin) {\n            if (!is_file($chemin)) {\n                continue;\n            }\n\n            $nom = basename($chemin);\n\n            $fichiers[] = [\n                'nom' => $nom,\n                'taille' => filesize($chemin) ?: 0,\n                'referenceValide' => (bool) preg_match('/^\\d+[-_]/', $nom),\n            ];\n        }\n\n        return $this->render('commande_fichiers/dossier_partage.html.twig', [\n            'fichiers' => $fichiers,\n            'cheminDossier' => $this->dossierPartage,\n        ]);\n    }\n\n    #[Route(\n        '/dossier-partage/importer',\n        name: 'app_fichier_dossier_partage_importer',\n        methods: ['POST']\n    )]\n    public function importerDossierPartage(\n        Request $request,\n        CommandesDetailsRepository $commandesDetailsRepository,\n        EntityManagerInterface $entityManager\n    ): Response {\n        $this->denyAccessUnlessGranted('ROLE_ADMIN');\n\n        if (!$this->isCsrfTokenValid(\n            'dossier-partage-importer',\n            (string) $request->request->get('_token')\n        )) {\n            $this->addFlash(\n                'error',\n                'Jeton de sécurité invalide, merci de réessayer.'\n            );\n\n            return $this->redirectToRoute('app_fichier_dossier_partage');\n        }\n\n        $importes = [];\n        $ignores = [];\n\n        foreach (glob($this->dossierPartage.'/*') ?: [] as $chemin) {\n            if (!is_file($chemin)) {\n                continue;\n            }\n\n            $nom = basename($chemin);\n\n            /*\n             * Convention de nommage attendue :\n             * <id du travail>_nom-du-fichier.ext\n             * ou <id du travail>-nom-du-fichier.ext\n             *\n             * L'id du travail est affiché sur la fiche de la\n             * commande (« Réf: #123 ») à côté de chaque travail.\n             */\n            if (!preg_match('/^(\\d+)[-_](.+)$/', $nom, $correspondances)) {\n                $ignores[] = $nom.' (nom sans référence de travail en préfixe)';\n                continue;\n            }\n\n            $detailId = (int) $correspondances[1];\n            $nomOriginal = $correspondances[2];\n\n            $detail = $commandesDetailsRepository->find($detailId);\n\n            if ($detail === null) {\n                $ignores[] = $nom.' (aucun travail avec la référence #'.$detailId.')';\n                continue;\n            }\n\n            $extension = strtolower(\n                pathinfo($nomOriginal, PATHINFO_EXTENSION)\n            );\n\n            $nomStockage = bin2hex(random_bytes(32));\n\n            if ($extension !== '') {\n                $nomStockage .= '.'.preg_replace(\n                    '/[^a-z0-9]/i',\n                    '',\n                    $extension\n                );\n            }\n\n            $cheminFinal = $this->dossierFinal.'/'.$nomStockage;\n\n            /*\n             * rename() déplace le fichier sans le recopier : même\n             * un fichier de plusieurs Go est instantané, puisque\n             * le dossier partagé et le dossier final sont sur le\n             * même disque.\n             */\n            if (!rename($chemin, $cheminFinal)) {\n                $ignores[] = $nom.' (impossible de déplacer le fichier)';\n                continue;\n            }\n\n            $typeMime = mime_content_type($cheminFinal);\n\n            $fichier = (new CommandeDetailFichier())\n                ->setJetonUpload(bin2hex(random_bytes(32)))\n                ->setCommandeDetail($detail)\n                ->setNomOriginal($nomOriginal)\n                ->setNomStockage($nomStockage)\n                ->setTypeMime(\n                    is_string($typeMime) ? $typeMime : 'application/octet-stream'\n                )\n                ->setTaille((int) (filesize($cheminFinal) ?: 0))\n                ->setNombreMorceaux(1)\n                ->setMorceauxRecus(1)\n                ->marquerUploadTermine();\n\n            $entityManager->persist($fichier);\n\n            $importes[] = $nomOriginal.' → travail #'.$detailId;\n        }\n\n        $entityManager->flush();\n\n        if ($importes !== []) {\n            $this->addFlash(\n                'success',\n                count($importes).' fichier(s) importé(s) : '.implode(', ', $importes)\n            );\n        }\n\n        if ($ignores !== []) {\n            $this->addFlash(\n                'error',\n                count($ignores).' fichier(s) ignoré(s) : '.implode(', ', $ignores)\n            );\n        }\n\n        if ($importes === [] && $ignores === []) {\n            $this->addFlash(\n                'success',\n                'Le dossier partagé est vide, rien à importer.'\n            );\n        }\n\n        return $this->redirectToRoute('app_fichier_dossier_partage');\n    }\n\n    private function assemblerFichier(\n",
        "routes dossier partage + import"
    ),
]

BASE_PAIRES = [
    (
        '<a href="{{ path( \'app_lot_etiquette_index\' ) }}" class="slide-item">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tLots d\'étiquettes\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>',
        '<a href="{{ path( \'app_lot_etiquette_index\' ) }}" class="slide-item">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tLots d\'étiquettes\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>\n\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t<a href="{{ path( \'app_fichier_dossier_partage\' ) }}" class="slide-item">\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t\tDossier partagé (import fichiers)\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t</a>',
        "lien de menu Dossier partage"
    ),
]

SHOW_PAIRES = [
    (
        '<small class="text-primary">\n\n\t\t\t\t\t\t\t\t\t\t\t\tTravail n°\n\t\t\t\t\t\t\t\t\t\t\t\t{{ loop.index }}\n\n\t\t\t\t\t\t\t\t\t\t\t</small>',
        '<small class="text-primary">\n\n\t\t\t\t\t\t\t\t\t\t\t\tTravail n°\n\t\t\t\t\t\t\t\t\t\t\t\t{{ loop.index }}\n\n\t\t\t\t\t\t\t\t\t\t\t</small>\n\n\t\t\t\t\t\t\t\t\t\t\t<small class="text-muted d-block" title="À utiliser en préfixe du nom de fichier pour l\'import depuis le dossier partagé">\n\n\t\t\t\t\t\t\t\t\t\t\t\tRéf: #{{ detail.id }}\n\n\t\t\t\t\t\t\t\t\t\t\t</small>',
        "numero Ref sur chaque travail"
    ),
]

NOUVEAU_TEMPLATE = '{% extends \'base.html.twig\' %}\n\n{% block title %}\n\tDossier partagé\n{% endblock %}\n\n{% block body %}\n\n\t<div class="side-app">\n\n\t\t{# ==========================================================\n\t\t\t\t\t\t\t\t       PAGE HEADER\n\t\t\t\t\t\t\t\t       ========================================================== #}\n\t\t<div class="page-header">\n\n\t\t\t<ol class="breadcrumb">\n\t\t\t\t<li class="breadcrumb-item">\n\t\t\t\t\t<a href="#">Paramètres</a>\n\t\t\t\t</li>\n\n\t\t\t\t<li class="breadcrumb-item active" aria-current="page">\n\t\t\t\t\tDossier partagé\n\t\t\t\t</li>\n\t\t\t</ol>\n\n\t\t</div>\n\t\t{# PAGE HEADER END #}\n\n\n\t\t<div class="row row-cards">\n\n\t\t\t<div class="col-lg-12">\n\n\t\t\t\t<div class="card mb-4">\n\n\t\t\t\t\t<div class="card-header">\n\t\t\t\t\t\t<h4 class="card-title">\n\t\t\t\t\t\t\tComment ça marche\n\t\t\t\t\t\t</h4>\n\t\t\t\t\t</div>\n\n\t\t\t\t\t<div class="card-body">\n\n\t\t\t\t\t\t<p>\n\t\t\t\t\t\t\tCe dossier sert de solution de secours quand l\'envoi d\'un fichier\n\t\t\t\t\t\t\téchoue depuis la fiche d\'une commande (gros fichiers, connexion\n\t\t\t\t\t\t\tinstable...).\n\t\t\t\t\t\t</p>\n\n\t\t\t\t\t\t<ol>\n\t\t\t\t\t\t\t<li>\n\t\t\t\t\t\t\t\tPartagez ce dossier sur le réseau (clic droit → Propriétés →\n\t\t\t\t\t\t\t\tPartage) si ce n\'est pas déjà fait :\n\t\t\t\t\t\t\t\t<code>{{ cheminDossier }}</code>\n\t\t\t\t\t\t\t</li>\n\n\t\t\t\t\t\t\t<li>\n\t\t\t\t\t\t\t\tSur la fiche de la commande, notez le numéro\n\t\t\t\t\t\t\t\t<strong>Réf: #...</strong> affiché à côté du travail concerné.\n\t\t\t\t\t\t\t</li>\n\n\t\t\t\t\t\t\t<li>\n\t\t\t\t\t\t\t\tDéposez le fichier dans ce dossier en renommant son nom pour\n\t\t\t\t\t\t\t\tqu\'il commence par ce numéro, suivi d\'un tiret ou d\'un\n\t\t\t\t\t\t\t\tunderscore. Exemple : <code>123_logo-client.pdf</code> pour le\n\t\t\t\t\t\t\t\ttravail Réf: #123.\n\t\t\t\t\t\t\t</li>\n\n\t\t\t\t\t\t\t<li>\n\t\t\t\t\t\t\t\tRevenez sur cette page et cliquez sur « Lancer l\'import ». Le\n\t\t\t\t\t\t\t\tfichier sera rattaché automatiquement au bon travail, comme\n\t\t\t\t\t\t\t\ts\'il avait été envoyé normalement.\n\t\t\t\t\t\t\t</li>\n\t\t\t\t\t\t</ol>\n\n\t\t\t\t\t\t<div class="alert alert-warning mb-0">\n\t\t\t\t\t\t\t<i class="fa fa-exclamation-triangle mr-2"></i>\n\t\t\t\t\t\t\tUn fichier sans numéro en préfixe, ou dont le numéro ne\n\t\t\t\t\t\t\tcorrespond à aucun travail, restera dans le dossier et\n\t\t\t\t\t\t\tapparaîtra ci-dessous en rouge après un import.\n\t\t\t\t\t\t</div>\n\n\t\t\t\t\t</div>\n\n\t\t\t\t</div>\n\n\n\t\t\t\t<div class="card">\n\n\t\t\t\t\t<div class="card-header d-flex justify-content-between align-items-center">\n\t\t\t\t\t\t<h4 class="card-title">\n\t\t\t\t\t\t\tFichiers en attente dans le dossier\n\t\t\t\t\t\t</h4>\n\n\t\t\t\t\t\t<form method="post" action="{{ path(\'app_fichier_dossier_partage_importer\') }}">\n\t\t\t\t\t\t\t<input type="hidden" name="_token" value="{{ csrf_token(\'dossier-partage-importer\') }}">\n\n\t\t\t\t\t\t\t<button type="submit" class="btn btn-success" {{ fichiers is empty ? \'disabled\' : \'\' }}>\n\t\t\t\t\t\t\t\t<i class="fa fa-download mr-1"></i>\n\t\t\t\t\t\t\t\tLancer l\'import\n\t\t\t\t\t\t\t</button>\n\t\t\t\t\t\t</form>\n\t\t\t\t\t</div>\n\n\t\t\t\t\t<div class="card-body">\n\n\t\t\t\t\t\t{% if fichiers is empty %}\n\n\t\t\t\t\t\t\t<p class="text-muted mb-0">\n\t\t\t\t\t\t\t\tLe dossier partagé est vide pour le moment.\n\t\t\t\t\t\t\t</p>\n\n\t\t\t\t\t\t{% else %}\n\n\t\t\t\t\t\t\t<div class="list-group">\n\n\t\t\t\t\t\t\t\t{% for fichier in fichiers %}\n\n\t\t\t\t\t\t\t\t\t<div class="list-group-item d-flex justify-content-between align-items-center">\n\n\t\t\t\t\t\t\t\t\t\t<div>\n\t\t\t\t\t\t\t\t\t\t\t{% if not fichier.referenceValide %}\n\t\t\t\t\t\t\t\t\t\t\t\t<i class="fa fa-exclamation-triangle text-danger mr-2"></i>\n\t\t\t\t\t\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t\t\t\t\t\t\t{{ fichier.nom }}\n\t\t\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t\t\t<span class="text-muted">\n\t\t\t\t\t\t\t\t\t\t\t{{ (fichier.taille / 1024 / 1024)|number_format(1, \',\', \' \') }} Mo\n\t\t\t\t\t\t\t\t\t\t</span>\n\n\t\t\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t\t\t{% endfor %}\n\n\t\t\t\t\t\t\t</div>\n\n\t\t\t\t\t\t{% endif %}\n\n\t\t\t\t\t</div>\n\n\t\t\t\t</div>\n\n\t\t\t</div>\n\n\t\t</div>\n\n\t</div>\n\n{% endblock %}\n'


def creer_template(racine):
    chemin_relatif = "templates/commande_fichiers/dossier_partage.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if os.path.isfile(chemin_absolu):
        contenu_existant = lire(chemin_absolu)
        if contenu_existant == NOUVEAU_TEMPLATE:
            print("[SKIP] " + chemin_relatif + " (deja applique)")
            return True
        else:
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


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    resultats = []

    print("-" * 70)
    print("src/Controller/FichierUploadController.php")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "src/Controller/FichierUploadController.php", CTRL_PAIRES))
    print()

    print("-" * 70)
    print("templates/commandes/show.html.twig")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "templates/commandes/show.html.twig", SHOW_PAIRES))
    print()

    print("-" * 70)
    print("templates/base.html.twig")
    print("-" * 70)
    resultats.append(appliquer_paires(racine, "templates/base.html.twig", BASE_PAIRES))
    print()

    print("-" * 70)
    print("templates/commande_fichiers/dossier_partage.html.twig (nouveau)")
    print("-" * 70)
    resultats.append(creer_template(racine))
    print()

    chemin_controller = os.path.join(racine, "src/Controller/FichierUploadController.php")
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_controller],
            capture_output=True, text=True, timeout=30
        )
        print("php -l FichierUploadController.php : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place.")
        print()
        print("Prochaines etapes :")
        print("  1. php bin/console cache:clear")
        print("  2. Partagez le dossier suivant sur le reseau Windows")
        print("     (clic droit dessus -> Proprietes -> Partage) :")
        print("       var/uploads/dossier_partage")
        print("     (dans le dossier du projet, a cote de var/uploads/commandes)")
        print("  3. Allez dans Parametres > Dossier partage pour verifier")
        print("     que la page s'affiche.")
        print()
        print("Utilisation :")
        print("  - Sur la fiche d'une commande, chaque travail affiche")
        print("    maintenant 'Ref: #123' a cote de 'Travail n(deg)...'.")
        print("  - Deposez le fichier dans le dossier partage en le")
        print("    renommant '123_nom-du-fichier.pdf' (numero + tiret ou")
        print("    underscore + nom).")
        print("  - Allez dans Parametres > Dossier partage et cliquez sur")
        print("    'Lancer l'import'.")
    else:
        print("Un ou plusieurs fichiers n'ont pas pu etre modifies (voir [ECHEC]/[ATTENTION] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()