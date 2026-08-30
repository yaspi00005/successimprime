#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envoi par morceaux pour "Ajouter un fichier traité" en pre-presse.

Les fichiers traites (TIFF haute resolution, scans...) sont souvent
tres volumineux. Au lieu d'un envoi en un seul bloc (limite par
upload_max_filesize/post_max_size de PHP, souvent trop bas), le
fichier est desormais decoupe en petits morceaux de 5 Mo cote
navigateur, chacun envoye comme une requete independante et
reassemble cote serveur une fois tous les morceaux recus -- exactement
le meme principe que le systeme deja utilise pour les fichiers
ORIGINAUX du client (FichierUploadController), mais applique ici au
circuit "fichier traite" (public/uploads/prepresse/...).

Si un fichier est deja selectionne dans le champ "Fichier traite" au
moment de soumettre le formulaire, l'envoi par morceaux prend le
relais automatiquement ; sinon (ou si JavaScript est desactive), le
formulaire classique (ajouterFichierTraite) continue de fonctionner
normalement en secours.

3 endroits modifies :
  1) src/Controller/ControlePrePresseController.php : nouvel import +
     2 nouvelles routes (initialiser / envoyer un morceau) + une
     methode privee d'assemblage.
  2) templates/controle_pre_presse/controler.html.twig : le formulaire
     "form-fichier-traite" recoit les URLs necessaires en attributs
     data-*.
  3) Le meme fichier twig recoit le JavaScript qui decoupe et envoie
     le fichier par morceaux.

Usage:
    python3 ajouter_upload_morceaux_fichier_traite.py /chemin/vers/successImprim
"""

import os
import re
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


def php_lint(chemin_absolu):
    try:
        resultat = subprocess.run(
            ["php", "-l", chemin_absolu],
            capture_output=True, text=True, timeout=30
        )
        print("  php -l : " + resultat.stdout.strip() + resultat.stderr.strip())
    except Exception:
        pass


# ============================================================
# 1) src/Controller/ControlePrePresseController.php
# ============================================================

ANCIEN_IMPORT = "use App\\Repository\\CommandesDetailsRepository;"
NOUVEL_IMPORT = "use App\\Repository\\CommandeDetailFichierRepository;\nuse App\\Repository\\CommandesDetailsRepository;"

ANCIENNE_FIN_METHODE = """        return $this->redirectToRoute(
            'app_controle_pre_presse_controler',
            ['id' => $detail->getId()]
        );
    }
"""

NOUVELLE_FIN_METHODE = """        return $this->redirectToRoute(
            'app_controle_pre_presse_controler',
            ['id' => $detail->getId()]
        );
    }

    /*
     * ============================================================
     * ENVOI PAR MORCEAUX (fichier traité)
     * ============================================================
     *
     * Les fichiers traités en pré-presse (TIFF haute résolution,
     * scans...) peuvent être très volumineux. Plutôt que de dépendre
     * uniquement des réglages upload_max_filesize/post_max_size de
     * PHP (souvent trop bas par défaut, et pas toujours modifiables
     * facilement sur le serveur du client), l'envoi se fait ici
     * découpé en petits morceaux, sur le même principe que
     * FichierUploadController (déjà utilisé pour les fichiers
     * originaux du client) : chaque morceau est une requête HTTP
     * indépendante et légère, réassemblée une fois tous les morceaux
     * reçus. L'ancienne route ajouterFichierTraite() reste en place
     * en secours (si JavaScript est indisponible).
     */
    private const TAILLE_MAX_MORCEAUX = 600 * 1024 * 1024;
    private const NOMBRE_MORCEAUX_MAX = 10000;

    #[Route(
        '/travail/{id}/fichier-traite/initialiser',
        name: 'fichier_traite_initialiser',
        requirements: ['id' => '\\d+'],
        methods: ['POST']
    )]
    public function initialiserFichierTraite(
        CommandesDetails $detail,
        Request $request,
        EntityManagerInterface $entityManager,
        SluggerInterface $slugger
    ): JsonResponse {
        $utilisateur = $this->getUser();

        if (!$utilisateur instanceof User) {
            return $this->json(
                ['message' => 'Vous devez être connecté.'],
                Response::HTTP_UNAUTHORIZED
            );
        }

        if (!$this->isCsrfTokenValid(
            'ajouter_fichier_traite_' . $detail->getId(),
            (string) $request->headers->get('X-CSRF-TOKEN')
        )) {
            return $this->json(
                ['message' => 'Jeton de sécurité invalide.'],
                Response::HTTP_FORBIDDEN
            );
        }

        try {
            $donnees = $request->toArray();
        } catch (\\Throwable) {
            return $this->json(
                ['message' => 'Le corps JSON de la requête est invalide.'],
                Response::HTTP_BAD_REQUEST
            );
        }

        $nomOriginal = trim((string) ($donnees['nom'] ?? ''));
        $typeMime = trim((string) ($donnees['typeMime'] ?? ''))
            ?: 'application/octet-stream';
        $taille = (int) ($donnees['taille'] ?? 0);
        $nombreMorceaux = (int) ($donnees['nombreMorceaux'] ?? 0);
        $fichierSourceId = (int) ($donnees['fichierSource'] ?? 0);

        if (
            $nomOriginal === ''
            || $taille <= 0
            || $taille > self::TAILLE_MAX_MORCEAUX
            || $nombreMorceaux <= 0
            || $nombreMorceaux > self::NOMBRE_MORCEAUX_MAX
        ) {
            return $this->json(
                ['message' => 'Informations du fichier invalides.'],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }

        $fichierSource = null;

        foreach ($detail->getFichiers() as $fichierDetail) {
            if ($fichierDetail->getId() === $fichierSourceId) {
                $fichierSource = $fichierDetail;
                break;
            }
        }

        if (!$fichierSource instanceof CommandeDetailFichier) {
            return $this->json(
                ['message' => 'Sélectionnez le fichier original correspondant.'],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }

        $nomSansExtension = pathinfo($nomOriginal, PATHINFO_FILENAME);
        $nomSecurise = $slugger->slug($nomSansExtension)->lower();
        $extension = strtolower(pathinfo($nomOriginal, PATHINFO_EXTENSION)) ?: 'bin';

        $jeton = bin2hex(random_bytes(32));

        $nomStockage = sprintf(
            '%s-v%d-%s.%s',
            $nomSecurise,
            $fichierSource->getVersion() + 1,
            bin2hex(random_bytes(8)),
            $extension
        );

        $repertoireRelatif = sprintf(
            'uploads/prepresse/commande_%d/detail_%d',
            $detail->getCommande()->getId(),
            $detail->getId()
        );

        /*
         * Préfixe la désignation de la ligne de commande, comme pour
         * l'envoi classique (ajouterFichierTraite).
         */
        $designationDetail = trim((string) $detail->getDesignation());

        $nomOriginalAffiche = $designationDetail !== ''
            ? sprintf('%s - %s', $designationDetail, $nomOriginal)
            : $nomOriginal;

        $face = trim((string) ($donnees['face'] ?? ''));
        $designationFichier = trim((string) ($donnees['designation'] ?? ''));

        $fichierTraite = new CommandeDetailFichier();

        $fichierTraite
            ->setJetonUpload($jeton)
            ->setCommandeDetail($detail)
            ->setFichierSource($fichierSource)
            ->setNomOriginal($nomOriginalAffiche)
            ->setNomStockage($nomStockage)
            ->setChemin($repertoireRelatif . '/' . $nomStockage)
            ->setTypeMime($typeMime)
            ->setTaille($taille)
            ->setNombreMorceaux($nombreMorceaux)
            ->setMorceauxRecus(0)
            ->setStatut(CommandeDetailFichier::STATUT_EN_COURS)
            ->setOrigine(CommandeDetailFichier::ORIGINE_INTERNE)
            ->setEtat(CommandeDetailFichier::ETAT_TRAITE)
            ->setVersion($fichierSource->getVersion() + 1)
            ->setFace($face !== '' ? $face : $fichierSource->getFace())
            ->setDesignation($designationFichier !== '' ? $designationFichier : 'Fichier traité')
            ->setGroupeFichier($fichierSource->getGroupeFichier())
            ->setQuantiteAProduire($fichierSource->getQuantiteAProduire())
            ->setObservation(
                trim((string) ($donnees['observation'] ?? '')) ?: null
            )
            ->setAjoutePar($utilisateur);

        $detail->addFichier($fichierTraite);

        $entityManager->persist($fichierTraite);
        $entityManager->flush();

        return $this->json([
            'jeton' => $jeton,
            'morceauxRecus' => 0,
            'nombreMorceaux' => $nombreMorceaux,
        ], Response::HTTP_CREATED);
    }

    #[Route(
        '/fichier-traite/{jeton}/morceaux/{index}',
        name: 'fichier_traite_morceau',
        requirements: [
            'jeton' => '[a-f0-9]{64}',
            'index' => '\\d+',
        ],
        methods: ['POST']
    )]
    public function envoyerMorceauFichierTraite(
        string $jeton,
        int $index,
        Request $request,
        CommandeDetailFichierRepository $repository,
        EntityManagerInterface $entityManager
    ): JsonResponse {
        $utilisateur = $this->getUser();

        if (!$utilisateur instanceof User) {
            return $this->json(
                ['message' => 'Vous devez être connecté.'],
                Response::HTTP_UNAUTHORIZED
            );
        }

        $fichier = $repository->findOneBy(['jetonUpload' => $jeton]);

        if (!$fichier instanceof CommandeDetailFichier) {
            return $this->json(
                ['message' => 'Session d’upload introuvable.'],
                Response::HTTP_NOT_FOUND
            );
        }

        $detailId = $fichier->getCommandeDetail()?->getId();

        if (
            $detailId === null
            || !$this->isCsrfTokenValid(
                'ajouter_fichier_traite_' . $detailId,
                (string) $request->headers->get('X-CSRF-TOKEN')
            )
        ) {
            return $this->json(
                ['message' => 'Jeton de sécurité invalide.'],
                Response::HTTP_FORBIDDEN
            );
        }

        if ($fichier->getStatut() === CommandeDetailFichier::STATUT_TERMINE) {
            return $this->json([
                'jeton' => $jeton,
                'statut' => CommandeDetailFichier::STATUT_TERMINE,
                'progression' => 100,
            ]);
        }

        $nombreMorceaux = $fichier->getNombreMorceaux();

        if (
            $nombreMorceaux === null
            || $index < 0
            || $index >= $nombreMorceaux
        ) {
            return $this->json(
                ['message' => 'Index du morceau invalide.'],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }

        /** @var UploadedFile|null $morceau */
        $morceau = $request->files->get('morceau');

        if (!$morceau instanceof UploadedFile || !$morceau->isValid()) {
            return $this->json(
                ['message' => 'Morceau absent ou invalide.'],
                Response::HTTP_UNPROCESSABLE_ENTITY
            );
        }

        $dossierTemporaire = $this->getParameter('kernel.project_dir')
            . '/var/uploads/prepresse_tmp/' . $jeton;

        if (
            !is_dir($dossierTemporaire)
            && !mkdir($dossierTemporaire, 0775, true)
            && !is_dir($dossierTemporaire)
        ) {
            return $this->json(
                ['message' => 'Impossible de créer le dossier temporaire.'],
                Response::HTTP_INTERNAL_SERVER_ERROR
            );
        }

        $cheminMorceau = $dossierTemporaire . '/' . sprintf('%08d.part', $index);

        /*
         * Si le morceau existe déjà, on ne le compte pas deux fois :
         * cela permet de reprendre un transfert interrompu.
         */
        if (!is_file($cheminMorceau)) {
            $morceau->move($dossierTemporaire, basename($cheminMorceau));
        }

        $morceauxRecus = count(glob($dossierTemporaire . '/*.part') ?: []);

        $fichier->setMorceauxRecus($morceauxRecus);

        if ($morceauxRecus === $nombreMorceaux) {
            try {
                $this->assemblerFichierTraite($fichier, $dossierTemporaire);
            } catch (\\Throwable $exception) {
                return $this->json(
                    ['message' => $exception->getMessage()],
                    Response::HTTP_INTERNAL_SERVER_ERROR
                );
            }
        }

        $entityManager->flush();

        $progression = (int) floor(
            ($fichier->getMorceauxRecus() / $nombreMorceaux) * 100
        );

        return $this->json([
            'jeton' => $jeton,
            'morceauxRecus' => $fichier->getMorceauxRecus(),
            'nombreMorceaux' => $nombreMorceaux,
            'progression' => min(100, $progression),
            'statut' => $fichier->getStatut(),
        ]);
    }

    private function assemblerFichierTraite(
        CommandeDetailFichier $fichier,
        string $dossierTemporaire
    ): void {
        $projet = (string) $this->getParameter('kernel.project_dir');
        $chemin = (string) $fichier->getChemin();

        $repertoireAbsolu = $projet . '/public/' . dirname($chemin);

        if (
            !is_dir($repertoireAbsolu)
            && !mkdir($repertoireAbsolu, 0775, true)
            && !is_dir($repertoireAbsolu)
        ) {
            throw new \\RuntimeException(
                'Impossible de créer le dossier final.'
            );
        }

        $cheminFinal = $projet . '/public/' . $chemin;
        $cheminAssemblage = $cheminFinal . '.assemblage';

        $sortie = fopen($cheminAssemblage, 'wb');

        if ($sortie === false) {
            throw new \\RuntimeException(
                'Impossible de créer le fichier final.'
            );
        }

        try {
            for (
                $index = 0;
                $index < (int) $fichier->getNombreMorceaux();
                $index++
            ) {
                $cheminMorceau = $dossierTemporaire . '/' . sprintf('%08d.part', $index);

                if (!is_file($cheminMorceau)) {
                    throw new \\RuntimeException(
                        sprintf('Le morceau %d est absent.', $index)
                    );
                }

                $entree = fopen($cheminMorceau, 'rb');

                if ($entree === false) {
                    throw new \\RuntimeException(
                        sprintf('Impossible de lire le morceau %d.', $index)
                    );
                }

                stream_copy_to_stream($entree, $sortie);
                fclose($entree);
            }
        } catch (\\Throwable $exception) {
            @unlink($cheminAssemblage);
            throw $exception;
        } finally {
            fclose($sortie);
        }

        $tailleReelle = filesize($cheminAssemblage);

        if ($tailleReelle === false || $tailleReelle !== $fichier->getTaille()) {
            @unlink($cheminAssemblage);

            throw new \\RuntimeException(
                'La taille du fichier assemblé est incorrecte.'
            );
        }

        if (!rename($cheminAssemblage, $cheminFinal)) {
            @unlink($cheminAssemblage);
            throw new \\RuntimeException(
                'Impossible de finaliser le fichier assemblé.'
            );
        }

        $typeMime = mime_content_type($cheminFinal);

        if (is_string($typeMime)) {
            $fichier->setTypeMime($typeMime);
        }

        $fichier->marquerUploadTermine();

        foreach (glob($dossierTemporaire . '/*.part') ?: [] as $morceau) {
            @unlink($morceau);
        }

        @rmdir($dossierTemporaire);
    }
"""

MARQUEUR_PHP = "fichier_traite_initialiser"


def corriger_controller(racine):
    chemin_relatif = "src/Controller/ControlePrePresseController.php"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_PHP in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja '" + MARQUEUR_PHP + "' (deja applique).")
        return True

    if ANCIEN_IMPORT not in contenu:
        print("[ECHEC] " + chemin_relatif + " : import CommandesDetailsRepository introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"^use App\\\\\\\\Repository\" " + chemin_relatif)
        return False

    if ANCIENNE_FIN_METHODE not in contenu:
        print("[ECHEC] " + chemin_relatif + " : fin de ajouterFichierTraite() introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n -A6 \"app_controle_pre_presse_controler'\" " + chemin_relatif + " | head -20")
        return False

    contenu_corrige = contenu.replace(ANCIEN_IMPORT, NOUVEL_IMPORT, 1)
    contenu_corrige = contenu_corrige.replace(ANCIENNE_FIN_METHODE, NOUVELLE_FIN_METHODE, 1)

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
    php_lint(chemin_absolu)
    return True


# ============================================================
# 2) templates/controle_pre_presse/controler.html.twig
# ============================================================

MARQUEUR_ID_FORM = '<form id="form-fichier-traite"'

BLOC_SET_TWIG = """{% set jetonTemporaireFichierTraite = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' %}
\t\t{% set indexTemporaireFichierTraite = 999999999 %}

\t\t{% set modeleUrlMorceauFichierTraite = path('app_controle_pre_presse_fichier_traite_morceau', {
\t\t\tjeton: jetonTemporaireFichierTraite,
\t\t\tindex: indexTemporaireFichierTraite
\t\t}) %}

\t\t{% set modeleUrlMorceauFichierTraite = modeleUrlMorceauFichierTraite|replace({
\t\t\t(jetonTemporaireFichierTraite): '__JETON__',
\t\t\t(indexTemporaireFichierTraite ~ ''): '__INDEX__'
\t\t}) %}

\t\t"""

ANCIEN_ACTION_FORM = "action=\"{{ path('app_controle_pre_presse_ajouter_fichier_traite', {id: detail.id}) }}\"></form>"
NOUVEL_ACTION_FORM = (
    "action=\"{{ path('app_controle_pre_presse_ajouter_fichier_traite', {id: detail.id}) }}\" "
    "data-upload-initialiser-url=\"{{ path('app_controle_pre_presse_fichier_traite_initialiser', {id: detail.id}) }}\" "
    "data-upload-morceau-url=\"{{ modeleUrlMorceauFichierTraite }}\"></form>"
)

BLOC_JS = """
document.addEventListener('DOMContentLoaded', function () {
/*
 * ============================================================
 * ENVOI PAR MORCEAUX (fichier traité)
 * ============================================================
 *
 * Les champs de ce formulaire ("fichierTraite", "fichierSource"...)
 * ne sont pas imbriqués dans <form id="form-fichier-traite"> : ils y
 * sont rattachés via l'attribut form="form-fichier-traite" (pour
 * éviter d'imbriquer deux <form> HTML sur cette page). Il faut donc
 * les retrouver par leur id ou par [form="form-fichier-traite"],
 * jamais par formulaire.querySelector(...).
 */
const formulaireFichierTraite = document.getElementById('form-fichier-traite');

if (!formulaireFichierTraite) {
return;
}

const initialiserUrl = formulaireFichierTraite.dataset.uploadInitialiserUrl;
const morceauUrlModele = formulaireFichierTraite.dataset.uploadMorceauUrl;

if (!initialiserUrl || !morceauUrlModele) {
return;
}

const TAILLE_MORCEAU_FICHIER_TRAITE = 5 * 1024 * 1024;

function construireUrlMorceauFichierTraite(jeton, index) {
return morceauUrlModele
.replace('__JETON__', jeton)
.replace('__INDEX__', String(index));
}

formulaireFichierTraite.addEventListener('submit', function (event) {
const champFichier = document.getElementById('fichierTraite');

if (!champFichier || !champFichier.files || !champFichier.files.length) {
return;
}

event.preventDefault();

const fichier = champFichier.files[0];

const champToken = document.querySelector('[form="form-fichier-traite"][name="_token"]');
const bouton = document.querySelector('[form="form-fichier-traite"][type="submit"]');
const champFichierSource = document.getElementById('fichierSource');
const champFace = document.getElementById('faceTraitee');
const champDesignation = document.getElementById('designationFichier');
const champObservation = document.getElementById('observationFichier');

const texteBoutonInitial = bouton ? bouton.innerHTML : '';

if (bouton) {
bouton.disabled = true;
bouton.innerHTML = '<i class="fa fa-spinner fa-spin mr-1"></i> Envoi en cours... 0 %';
}

(async function () {
try {

const jetonCsrf = champToken ? champToken.value : '';

const nombreMorceaux = Math.max(
1,
Math.ceil(fichier.size / TAILLE_MORCEAU_FICHIER_TRAITE)
);

const reponseInit = await fetch(initialiserUrl, {
method: 'POST',
headers: {
'Content-Type': 'application/json',
'X-CSRF-TOKEN': jetonCsrf,
Accept: 'application/json'
},
body: JSON.stringify({
nom: fichier.name,
typeMime: fichier.type || 'application/octet-stream',
taille: fichier.size,
nombreMorceaux: nombreMorceaux,
fichierSource: champFichierSource ? champFichierSource.value : '',
face: champFace ? champFace.value : '',
designation: champDesignation ? champDesignation.value : '',
observation: champObservation ? champObservation.value : ''
})
});

const donneesInit = await reponseInit.json();

if (!reponseInit.ok || !donneesInit.jeton) {
throw new Error(donneesInit.message || "Impossible d'initialiser l'envoi.");
}

const jeton = donneesInit.jeton;

for (let index = 0; index < nombreMorceaux; index++) {

const debut = index * TAILLE_MORCEAU_FICHIER_TRAITE;
const fin = Math.min(fichier.size, debut + TAILLE_MORCEAU_FICHIER_TRAITE);

const donneesMorceauFormulaire = new FormData();
donneesMorceauFormulaire.append('morceau', fichier.slice(debut, fin), fichier.name);

const reponseMorceau = await fetch(construireUrlMorceauFichierTraite(jeton, index), {
method: 'POST',
headers: {
'X-CSRF-TOKEN': jetonCsrf
},
body: donneesMorceauFormulaire
});

const donneesMorceau = await reponseMorceau.json();

if (!reponseMorceau.ok) {
throw new Error(donneesMorceau.message || "L'envoi du fichier a été interrompu.");
}

const progression = typeof donneesMorceau.progression === 'number'
? donneesMorceau.progression
: Math.round(((index + 1) / nombreMorceaux) * 100);

if (bouton) {
bouton.innerHTML = '<i class="fa fa-spinner fa-spin mr-1"></i> Envoi en cours... ' + progression + ' %';
}
}

window.location.reload();

} catch (erreur) {

console.error(erreur);

const messageErreur = erreur.message || 'Une erreur est survenue pendant l’envoi du fichier.';

if (typeof window.Swal !== 'undefined') {
window.Swal.fire({
icon: 'error',
title: 'Échec de l’envoi',
text: messageErreur
});
} else {
window.alert(messageErreur);
}

if (bouton) {
bouton.disabled = false;
bouton.innerHTML = texteBoutonInitial;
}
}
})();
});
});
"""

MARQUEUR_TWIG = "ENVOI PAR MORCEAUX (fichier traité)"


def corriger_twig(racine):
    chemin_relatif = "templates/controle_pre_presse/controler.html.twig"
    chemin_absolu = os.path.join(racine, chemin_relatif)

    print()
    print("-" * 70)
    print(chemin_relatif)
    print("-" * 70)

    if not os.path.isfile(chemin_absolu):
        print("[ABSENT] " + chemin_relatif + " n'existe pas du tout sur le disque.")
        return False

    with open(chemin_absolu, "r", encoding="utf-8") as f:
        contenu = f.read()

    if MARQUEUR_TWIG in contenu:
        print("[SKIP] " + chemin_relatif + " contient deja la logique d'envoi par morceaux (deja applique).")
        return True

    if MARQUEUR_ID_FORM not in contenu:
        print("[ECHEC] " + chemin_relatif + " : <form id=\"form-fichier-traite\"> introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"form-fichier-traite\" " + chemin_relatif + " | head -5")
        return False

    if ANCIEN_ACTION_FORM not in contenu:
        print("[ECHEC] " + chemin_relatif + " : attribut action= du formulaire introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    grep -n \"form-fichier-traite\" " + chemin_relatif + " | head -5")
        return False

    motif_fin_script = re.compile(r"[ \t]*</script>[ \t]*\n\{%-?\s*endblock\s*-?%\}\s*\Z")

    if not motif_fin_script.search(contenu):
        print("[ECHEC] " + chemin_relatif + " : fin du bloc javascripts (</script>{% endblock %}) introuvable -> abandon (rien ecrit).")
        print("  Copiez-moi le resultat de :")
        print("    tail -10 " + chemin_relatif)
        return False

    contenu_corrige = contenu.replace(
        MARQUEUR_ID_FORM,
        BLOC_SET_TWIG + MARQUEUR_ID_FORM,
        1
    )

    contenu_corrige = contenu_corrige.replace(
        ANCIEN_ACTION_FORM,
        NOUVEL_ACTION_FORM,
        1
    )

    def _inserer_js(m):
        return BLOC_JS.strip("\n") + "\n" + m.group(0)

    contenu_corrige, nb_fin = motif_fin_script.subn(_inserer_js, contenu_corrige, count=1)

    if nb_fin == 0:
        print("[ECHEC] " + chemin_relatif + " : impossible d'inserer le JavaScript -> abandon (rien ecrit).")
        return False

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

    resultats = [
        corriger_controller(racine),
        corriger_twig(racine),
    ]

    print()
    print("=" * 70)
    print("RESUME")
    print("=" * 70)

    if all(resultats):
        print("Tout est en place. Lancez maintenant :")
        print("  php bin/console cache:clear")
        print()
        print("Puis videz le cache de votre navigateur (Cmd+Maj+R). Dans")
        print("'Ajouter un fichier traité', un fichier volumineux part")
        print("maintenant par petits morceaux de 5 Mo, avec une barre de")
        print("progression sur le bouton d'envoi, au lieu d'un seul envoi")
        print("limite par la configuration PHP du serveur.")
    else:
        print("Au moins un fichier n'a pas pu etre modifie (voir [ECHEC] ci-dessus).")
        print("Recopiez-moi TOUT ce resume, je corrige avant de vous renvoyer le script.")


if __name__ == "__main__":
    main()
