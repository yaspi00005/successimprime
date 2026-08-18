"""
Suite de supprimer_fichier_televerse.py : applique uniquement les
etapes 6 a 9 (l'etape 5 a deja ete appliquee separement via
fix_etape5_construireUrlSuppression.py, avec une mise en forme
legerement differente mais fonctionnellement identique).

Modifie :
- templates/commandes/_form.html.twig

A executer a la racine du dépôt : python3 supprimer_fichier_suite_6a9.py
"""

import sys

path = "templates/commandes/_form.html.twig"


def appliquer(old, new, label):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    if new in content:
        print(f"[SKIP] {label} : déjà présent")
        return

    count = content.count(old)
    if count != 1:
        print(f"[ERREUR] {label} : {count} occurrence(s) trouvée(s) (1 attendue)")
        sys.exit(1)

    content = content.replace(old, new)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] {label}")


appliquer(
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
    "6) JS : bouton supprimer dans creerLigneUpload()",
)

appliquer(
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
    "7) JS : retirerJetonFichier() + supprimerFichierTeleverse()",
)

appliquer(
    """const jeton = donneesInit.jeton;

for (let index = 0; index < nombreMorceaux; index++) {""",
    """const jeton = donneesInit.jeton;

/*
 * Rendu disponible sur la ligne pour le bouton de suppression :
 * on peut annuler un envoi meme avant qu'il soit termine.
 */
ligneUpload.dataset.jeton = jeton;

for (let index = 0; index < nombreMorceaux; index++) {""",
    "8) JS : ligneUpload.dataset.jeton",
)

appliquer(
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
    "9) JS : binding clic bouton supprimer",
)

print("\nTerminé.")
