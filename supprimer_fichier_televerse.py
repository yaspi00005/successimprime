"""
Ajoute la possibilité de supprimer un fichier déjà téléversé (ou en
cours d'envoi) dans la commande, avant l'enregistrement définitif.

- Nouvelle route/action POST /commande-fichiers/{jeton}/supprimer :
  supprime le fichier physique (assemblé ou morceaux en cours) et
  l'entrée CommandeDetailFichier correspondante. Refuse si le
  fichier est déjà rattaché à un détail de commande enregistré.
- Bouton "corbeille" sur chaque ligne de fichier téléversé, qui
  appelle cette route puis retire le jeton du champ caché
  jetonsFichiers et la ligne de la liste.

Modifie :
- src/Controller/FichierUploadController.php
- templates/commandes/_form.html.twig

A executer a la racine du dépôt : python3 supprimer_fichier_televerse.py
"""

import sys


def appliquer(path, old, new, label):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if new in content:
        print(f"[SKIP] {label} : déjà présent dans {path}")
        return

    count = content.count(old)
    if count != 1:
        print(f"[ERREUR] {label} : {count} occurrence(s) trouvée(s) dans {path} (1 attendue)")
        sys.exit(1)

    content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] {label} appliqué à {path}")


# ==================================================================
# 1) src/Controller/FichierUploadController.php
# ==================================================================
CONTROLLER = "src/Controller/FichierUploadController.php"

appliquer(
    CONTROLLER,
    """    #[Route(
        '/{id}/visualiser',""",
    """    #[Route(
        '/{jeton}/supprimer',
        name: 'app_fichier_upload_supprimer',
        requirements: [
            'jeton' => '[a-f0-9]{64}',
        ],
        methods: ['POST']
    )]
    public function supprimer(
        string $jeton,
        Request $request,
        CommandeDetailFichierRepository $repository,
        EntityManagerInterface $entityManager
    ): JsonResponse {
        if (!$this->isCsrfTokenValid(
            'upload-commande',
            $request->headers->get('X-CSRF-TOKEN')
        )) {
            return $this->json([
                'message' => 'Jeton CSRF invalide.',
            ], 403);
        }

        $fichier = $repository->findOneBy([
            'jetonUpload' => $jeton,
        ]);

        if (!$fichier) {
            return $this->json([
                'message' => 'Fichier introuvable.',
            ], 404);
        }

        /*
         * Un fichier déjà rattaché à un détail de commande
         * enregistré ne peut plus être supprimé par ce biais : il
         * ne s'agit alors plus d'un envoi en attente, mais d'une
         * pièce jointe d'une commande existante.
         */
        if ($fichier->getCommandeDetail() !== null) {
            return $this->json([
                'message' => 'Ce fichier est déjà rattaché à une commande enregistrée.',
            ], 409);
        }

        if ($fichier->getStatut() === 'TERMINE' && $fichier->getNomStockage()) {
            $chemin = $this->dossierFinal
                .'/'.basename($fichier->getNomStockage());

            if (is_file($chemin)) {
                @unlink($chemin);
            }
        }

        $dossierJeton = $this->dossierTemporaire.'/'.$jeton;

        if (is_dir($dossierJeton)) {
            foreach (glob($dossierJeton.'/*.part') ?: [] as $morceau) {
                @unlink($morceau);
            }

            @rmdir($dossierJeton);
        }

        $entityManager->remove($fichier);
        $entityManager->flush();

        return $this->json([
            'success' => true,
        ]);
    }

    #[Route(
        '/{id}/visualiser',""",
    "Route + action supprimer()",
)


# ==================================================================
# 2) templates/commandes/_form.html.twig
# ==================================================================
TPL = "templates/commandes/_form.html.twig"

appliquer(
    TPL,
    """{% set modeleUrlStatut =
    modeleUrlStatut|replace({
        (jetonTemporaire):
            '__JETON__'
    })
%}""",
    """{% set modeleUrlStatut =
    modeleUrlStatut|replace({
        (jetonTemporaire):
            '__JETON__'
    })
%}


{% set modeleUrlSuppression = path(
    'app_fichier_upload_supprimer',
    {
        jeton: jetonTemporaire
    }
) %}


{% set modeleUrlSuppression =
    modeleUrlSuppression|replace({
        (jetonTemporaire):
            '__JETON__'
    })
%}""",
    "Twig : modeleUrlSuppression",
)

appliquer(
    TPL,
    """        'data-upload-morceau-url':
            modeleUrlMorceau,

        'data-upload-statut-url':
            modeleUrlStatut
    }
}) }}""",
    """        'data-upload-morceau-url':
            modeleUrlMorceau,

        'data-upload-statut-url':
            modeleUrlStatut,

        'data-upload-supprimer-url':
            modeleUrlSuppression
    }
}) }}""",
    "Attribut data-upload-supprimer-url",
)

appliquer(
    TPL,
    """const uploadMorceauUrlModele = form.dataset.uploadMorceauUrl;

const uploadStatutUrlModele = form.dataset.uploadStatutUrl;""",
    """const uploadMorceauUrlModele = form.dataset.uploadMorceauUrl;

const uploadStatutUrlModele = form.dataset.uploadStatutUrl;

const uploadSupprimerUrlModele = form.dataset.uploadSupprimerUrl;""",
    "JS : const uploadSupprimerUrlModele",
)

appliquer(
    TPL,
    """function construireUrlMorceauUpload(jeton, index) {
return uploadMorceauUrlModele
.replace('__JETON__', jeton)
.replace('__INDEX__', String(index));
}""",
    """function construireUrlMorceauUpload(jeton, index) {
return uploadMorceauUrlModele
.replace('__JETON__', jeton)
.replace('__INDEX__', String(index));
}

function construireUrlSuppressionFichier(jeton) {
return uploadSupprimerUrlModele
.replace('__JETON__', jeton);
}""",
    "JS : construireUrlSuppressionFichier()",
)

appliquer(
    TPL,
    """ligne.appendChild(apercu);
ligne.appendChild(infos);

return ligne;
}

function ajouterJetonFichier(detail, jeton) {
const champ = detail.querySelector('.js-jetons-fichiers');""",
    """const boutonSupprimer = document.createElement('button');
boutonSupprimer.type = 'button';
boutonSupprimer.className = 'btn btn-sm btn-link text-danger js-upload-supprimer';
boutonSupprimer.title = 'Supprimer ce fichier';
boutonSupprimer.innerHTML = '<i class="fa fa-trash"></i>';

ligne.appendChild(apercu);
ligne.appendChild(infos);
ligne.appendChild(boutonSupprimer);

return ligne;
}

function ajouterJetonFichier(detail, jeton) {
const champ = detail.querySelector('.js-jetons-fichiers');""",
    "JS : bouton supprimer dans creerLigneUpload()",
)

appliquer(
    TPL,
    """champ.value = valeurs.join(',');
}

async function televerserFichier(detail, fichier, ligneUpload) {""",
    """champ.value = valeurs.join(',');
}

function retirerJetonFichier(detail, jeton) {
const champ = detail.querySelector('.js-jetons-fichiers');

if (! champ) {
return;
}

const valeurs = champ.value
? champ.value.split(',').map(function (v) { return v.trim(); }).filter(Boolean)
: [];

champ.value = valeurs.filter(function (v) { return v !== jeton; }).join(',');
}

async function supprimerFichierTeleverse(detail, ligne) {
const jeton = ligne.dataset.jeton || '';

const statutTexte = ligne.querySelector('.js-upload-statut');

/*
 * Pas encore de jeton (upload pas encore initialise cote serveur) :
 * rien a supprimer la-bas, on retire juste la ligne localement.
 */
if (! jeton) {
ligne.remove();

return;
}

if (! window.confirm('Supprimer ce fichier ?')) {
return;
}

if (statutTexte) {
statutTexte.textContent = 'Suppression...';
}

try {

const reponse = await fetch(construireUrlSuppressionFichier(jeton), {
method: 'POST',
headers: {
'X-CSRF-TOKEN': uploadCsrf
}
});

if (! reponse.ok) {
const donnees = await reponse.json().catch(function () { return {}; });

throw new Error(donnees.message || 'Impossible de supprimer ce fichier.');
}

retirerJetonFichier(detail, jeton);

ligne.remove();

} catch (erreur) {

console.error(erreur);

if (statutTexte) {
statutTexte.textContent = 'Échec : ' + erreur.message;
}
}
}

async function televerserFichier(detail, fichier, ligneUpload) {""",
    "JS : retirerJetonFichier() + supprimerFichierTeleverse()",
)

appliquer(
    TPL,
    """const jeton = donneesInit.jeton;

for (let index = 0; index < nombreMorceaux; index++) {""",
    """const jeton = donneesInit.jeton;

/*
 * Rendu disponible sur la ligne pour le bouton de suppression :
 * on peut annuler un envoi meme avant qu'il soit termine.
 */
ligneUpload.dataset.jeton = jeton;

for (let index = 0; index < nombreMorceaux; index++) {""",
    "JS : ligneUpload.dataset.jeton",
)

appliquer(
    TPL,
    """for (const fichier of fichiers) {

const ligne = creerLigneUpload(fichier);

zoneListe.appendChild(ligne);

await televerserFichier(detail, fichier, ligne);
}
});
}


function champDetail(detail, nom) {""",
    """for (const fichier of fichiers) {

const ligne = creerLigneUpload(fichier);

zoneListe.appendChild(ligne);

const boutonSupprimer = ligne.querySelector('.js-upload-supprimer');

if (boutonSupprimer) {
boutonSupprimer.addEventListener('click', function () {
supprimerFichierTeleverse(detail, ligne);
});
}

await televerserFichier(detail, fichier, ligne);
}
});
}


function champDetail(detail, nom) {""",
    "JS : binding clic bouton supprimer",
)

print("\nTerminé.")
