#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrige l'erreur 404 "Le fichier est introuvable sur le serveur" en
pre-presse (visualiser / telecharger un fichier traite).

Cause : les fichiers "traites" ajoutes via "Ajouter un fichier traite"
(ajouterFichierTraite) sont enregistres sous
public/uploads/prepresse/commande_X/detail_Y/... , alors que les
routes de visualisation et de telechargement (visualiserFichier /
telechargerFichier) ne cherchaient QUE dans var/uploads/commandes/
(le dossier utilise par l'upload des fichiers ORIGINAUX du client).
Resultat : impossible de visualiser ou telecharger un fichier traite
(TIFF, .cut, image, peu importe le format), meme s'il a bien ete
enregistre en base au moment de l'ajout -> d'ou l'impression que
"le fichier n'a pas ete uploade".

Ce script ajoute une methode privee resoudreCheminFichierStocke() qui
retrouve le fichier dans les DEUX emplacements possibles, et met a
jour visualiserFichier() et telechargerFichier() pour s'en servir.

Usage:
    python3 corriger_visualiser_fichier_traite.py /chemin/vers/successImprim
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


ANCIEN_BLOC_1 = """    #[Route(
        '/fichier/{id}/visualiser',
        name: 'visualiser_fichier',
        requirements: ['id' => '\\d+'],
        methods: ['GET']
    )]
    public function visualiserFichier(
        CommandeDetailFichier $fichier
    ): BinaryFileResponse {
        if (!$fichier->isActif()) {
            throw $this->createNotFoundException(
                'Le fichier demand\u00e9 est indisponible.'
            );
        }

        $projet = (string) $this->getParameter('kernel.project_dir');

        /*
     * R\u00e9pertoire r\u00e9el de stockage :
     * var/uploads/commandes
     */
        $racineStockage = $projet . '/var/uploads/commandes';
        $racineReelle = realpath($racineStockage);

        if ($racineReelle === false || !is_dir($racineReelle)) {
            throw $this->createNotFoundException(
                'Le r\u00e9pertoire de stockage est introuvable.'
            );
        }

        $nomStockage = basename(
            trim((string) $fichier->getNomStockage())
        );

        if ($nomStockage === '' || $nomStockage === '.') {
            throw $this->createNotFoundException(
                'Le nom de stockage du fichier est invalide.'
            );
        }

        $cheminRecherche = $racineStockage
            . DIRECTORY_SEPARATOR
            . $nomStockage;

        $cheminComplet = realpath($cheminRecherche);

        /*
     * S\u00e9curit\u00e9 :
     * le fichier doit obligatoirement rester dans
     * var/uploads/commandes.
     */
        if (
            $cheminComplet === false
            || !str_starts_with(
                $cheminComplet,
                $racineReelle . DIRECTORY_SEPARATOR
            )
            || !is_file($cheminComplet)
            || !is_readable($cheminComplet)
        ) {
            throw $this->createNotFoundException(
                'Le fichier est introuvable sur le serveur.'
            );
        }

        /*
     * D\u00e9tection r\u00e9elle du type MIME.
     * On ne d\u00e9pend pas seulement de la valeur enregistr\u00e9e en base.
     */
        $extension = strtolower(
            pathinfo($cheminComplet, PATHINFO_EXTENSION)
        );

        $extensionsImages = [
            'jpg',
            'jpeg',
            'png',
            'webp',
        ];

        if (in_array($extension, $extensionsImages, true)) {
            $racineApercus = $racineReelle
                . DIRECTORY_SEPARATOR
                . 'apercus';

            $cheminApercu = $racineApercus
                . DIRECTORY_SEPARATOR
                . basename($cheminComplet);

            if (is_file($cheminApercu) && is_readable($cheminApercu)) {
                $cheminComplet = $cheminApercu;
            }
        }"""

NOUVEAU_BLOC_1 = """    /*
     * Retrouve le chemin reel sur disque d'un fichier de commande,
     * quel que soit le circuit d'upload par lequel il est arrive :
     *   - fichiers "traites" en pre-presse (ajouterFichierTraite) :
     *     stockes sous public/{chemin} (chemin relatif enregistre
     *     en base) ;
     *   - fichiers originaux du client (FichierUploadController) :
     *     stockes a plat sous var/uploads/commandes/{nomStockage},
     *     sans valeur de "chemin" en base.
     * Sans ceci, seul le deuxieme circuit fonctionnait : visualiser
     * ou telecharger un fichier traite renvoyait une 404.
     */
    private function resoudreCheminFichierStocke(
        CommandeDetailFichier $fichier
    ): ?string {
        $projet = (string) $this->getParameter('kernel.project_dir');
        $chemin = trim((string) $fichier->getChemin());

        if ($chemin !== '') {
            $racinePublique = realpath($projet . '/public');

            if ($racinePublique !== false) {
                $cheminComplet = realpath(
                    $projet . '/public/' . $chemin
                );

                if (
                    $cheminComplet !== false
                    && str_starts_with(
                        $cheminComplet,
                        $racinePublique . DIRECTORY_SEPARATOR
                    )
                    && is_file($cheminComplet)
                    && is_readable($cheminComplet)
                ) {
                    return $cheminComplet;
                }
            }
        }

        /*
     * Repertoire reel de stockage (circuit historique) :
     * var/uploads/commandes
     */
        $racineStockage = $projet . '/var/uploads/commandes';
        $racineReelle = realpath($racineStockage);

        if ($racineReelle === false || !is_dir($racineReelle)) {
            return null;
        }

        $nomStockage = basename(
            trim((string) $fichier->getNomStockage())
        );

        if ($nomStockage === '' || $nomStockage === '.') {
            return null;
        }

        $cheminRecherche = $racineStockage
            . DIRECTORY_SEPARATOR
            . $nomStockage;

        $cheminComplet = realpath($cheminRecherche);

        /*
     * S\u00e9curit\u00e9 :
     * le fichier doit obligatoirement rester dans
     * var/uploads/commandes.
     */
        if (
            $cheminComplet === false
            || !str_starts_with(
                $cheminComplet,
                $racineReelle . DIRECTORY_SEPARATOR
            )
            || !is_file($cheminComplet)
            || !is_readable($cheminComplet)
        ) {
            return null;
        }

        /*
     * D\u00e9tection r\u00e9elle du type MIME.
     * On ne d\u00e9pend pas seulement de la valeur enregistr\u00e9e en base.
     */
        $extension = strtolower(
            pathinfo($cheminComplet, PATHINFO_EXTENSION)
        );

        $extensionsImages = [
            'jpg',
            'jpeg',
            'png',
            'webp',
        ];

        if (in_array($extension, $extensionsImages, true)) {
            $racineApercus = $racineReelle
                . DIRECTORY_SEPARATOR
                . 'apercus';

            $cheminApercu = $racineApercus
                . DIRECTORY_SEPARATOR
                . basename($cheminComplet);

            if (is_file($cheminApercu) && is_readable($cheminApercu)) {
                $cheminComplet = $cheminApercu;
            }
        }

        return $cheminComplet;
    }
    #[Route(
        '/fichier/{id}/visualiser',
        name: 'visualiser_fichier',
        requirements: ['id' => '\\d+'],
        methods: ['GET']
    )]
    public function visualiserFichier(
        CommandeDetailFichier $fichier
    ): BinaryFileResponse {
        if (!$fichier->isActif()) {
            throw $this->createNotFoundException(
                'Le fichier demand\u00e9 est indisponible.'
            );
        }

        $cheminComplet = $this->resoudreCheminFichierStocke($fichier);

        if ($cheminComplet === null) {
            throw $this->createNotFoundException(
                'Le fichier est introuvable sur le serveur.'
            );
        }"""

ANCIEN_BLOC_2 = """        if (!$fichier->isActif()) {
            throw $this->createNotFoundException(
                'Le fichier demand\u00e9 est indisponible.'
            );
        }

        $projet = (string) $this->getParameter('kernel.project_dir');
        $racineStockage = $projet . '/var/uploads/commandes';
        $racineReelle = realpath($racineStockage);

        if ($racineReelle === false || !is_dir($racineReelle)) {
            throw $this->createNotFoundException(
                'Le r\u00e9pertoire de stockage est introuvable.'
            );
        }

        $nomStockage = basename(
            trim((string) $fichier->getNomStockage())
        );

        if ($nomStockage === '' || $nomStockage === '.') {
            throw $this->createNotFoundException(
                'Le nom de stockage est invalide.'
            );
        }

        $cheminComplet = realpath(
            $racineReelle . DIRECTORY_SEPARATOR . $nomStockage
        );

        if (
            $cheminComplet === false
            || !str_starts_with(
                $cheminComplet,
                $racineReelle . DIRECTORY_SEPARATOR
            )
            || !is_file($cheminComplet)
            || !is_readable($cheminComplet)
        ) {
            throw $this->createNotFoundException(
                'Le fichier original est introuvable sur le serveur.'
            );
        }

        $nomOriginal = trim("""

NOUVEAU_BLOC_2 = """        if (!$fichier->isActif()) {
            throw $this->createNotFoundException(
                'Le fichier demand\u00e9 est indisponible.'
            );
        }

        $cheminComplet = $this->resoudreCheminFichierStocke($fichier);

        if ($cheminComplet === null) {
            throw $this->createNotFoundException(
                'Le fichier original est introuvable sur le serveur.'
            );
        }

        $nomOriginal = trim("""

MARQUEUR = "resoudreCheminFichierStocke"


def corriger_fichier(racine, chemin_relatif):
    chemin_absolu = os.path.join(racine, chemin_relatif)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + MARQUEUR + "' (deja applique).")
        return True

    contenu_original = contenu

    if ANCIEN_BLOC_1 not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc 1/2 (visualiserFichier) introuvable -> abandon (rien ecrit).")
        print("  Votre fichier reel differe probablement du brouillon a cet endroit.")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -A15 \"name: 'visualiser_fichier'\" " + chemin_relatif)
        return False

    contenu = contenu.replace(ANCIEN_BLOC_1, NOUVEAU_BLOC_1, 1)
    print("  Bloc 1/2 (visualiserFichier + nouvelle methode) : applique")

    if ANCIEN_BLOC_2 not in contenu:
        print("[ECHEC] " + chemin_relatif + " : bloc 2/2 (telechargerFichier) introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -A15 \"name: 'telecharger_fichier'\" " + chemin_relatif)
        return False

    contenu = contenu.replace(ANCIEN_BLOC_2, NOUVEAU_BLOC_2, 1)
    print("  Bloc 2/2 (telechargerFichier) : applique")

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

    print("[OK VERIFIE] " + chemin_relatif)
    print("  Chemin reel : " + os.path.realpath(chemin_absolu))

    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=30
        )
        print("  php -l : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass

    return True


def main():
    racine = sys.argv[1] if len(sys.argv) >= 2 else "."
    verifier_racine(racine)

    chemin_relatif = "src/Controller/ControlePrePresseController.php"

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
        print("Les fichiers traites ajoutes en pre-presse (TIFF, .cut, etc.)")
        print("doivent maintenant s'ouvrir/telecharger correctement au lieu")
        print("de renvoyer une erreur 404.")
        print()
        print("Si un fichier TIFF tres volumineux ne s'upload toujours pas")
        print("du tout (ni message d'erreur ni fichier enregistre), verifiez")
        print("upload_max_filesize et post_max_size dans php.ini (XAMPP :")
        print("C:\\xampp\\php\\php.ini), qui doivent etre au moins aussi grands")
        print("que la taille de vos plus gros fichiers, puis redemarrez Apache.")
    else:
        print("Le fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
