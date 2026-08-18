"""
Sauvegarde automatique en session de la saisie en cours d'une
commande ou d'un devis "nouveau" (pas encore enregistré), avec
proposition de restauration si la page se ferme ou plante avant
l'enregistrement définitif.

Nécessite le nouveau contrôleur src/Controller/BrouillonSaisieController.php
(livré séparément, à copier tel quel dans src/Controller/) et la
migration Version20260818140000.php n'est PAS nécessaire ici (les
brouillons vivent uniquement en session, aucune colonne en base).

Fonctionnement :
- Le formulaire s'auto-sauvegarde en session (débounce 4s après
  chaque frappe, plus un filet de sécurité toutes les 60s).
- Au chargement d'une commande/devis "nouveau", si un brouillon
  existe, une boîte de dialogue propose de le restaurer.
- La restauration recharge la page avec ?restaurer=1 : le
  contrôleur pré-remplit le formulaire à partir du brouillon en
  session (via $form->submit(), sans jamais déclencher
  l'enregistrement) — Symfony reconstruit alors correctement les
  lignes de détail dynamiques, comme pour n'importe quel formulaire
  invalide réaffiché.
- Le brouillon est supprimé de la session dès l'enregistrement
  réussi.

Modifie :
- src/Controller/CommandesController.php
- src/Controller/DevisController.php
- templates/commandes/_form.html.twig
- templates/devis/_form.html.twig

A executer a la racine du dépôt : python3 brouillon_session_commande_devis.py
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
# 1) src/Controller/CommandesController.php
# ==================================================================
CTRL_COMMANDE = "src/Controller/CommandesController.php"

appliquer(
    CTRL_COMMANDE,
    """        $commande = new Commandes();

        $form = $this->createForm(
            CommandesType::class,
            $commande
        );

        $form->handleRequest($request);""",
    """        $commande = new Commandes();

        $form = $this->createForm(
            CommandesType::class,
            $commande
        );

        /*
     * ============================================================
     * RESTAURATION D'UN BROUILLON
     * ============================================================
     *
     * Pré-remplit le formulaire à partir d'une saisie sauvegardée
     * automatiquement en session (voir BrouillonSaisieController),
     * sans jamais déclencher l'enregistrement : on affiche juste le
     * formulaire pré-rempli, l'agent doit re-soumettre lui-même.
     */
        if (
            $request->isMethod('GET')
            && $request->query->get('restaurer') === '1'
        ) {
            $brouillon = $request->getSession()->get('brouillon_commande');

            if (is_array($brouillon) && !empty($brouillon['champs'])) {
                $form->submit($brouillon['champs'], false);
            }

            return $this->render(
                'commandes/new.html.twig',
                [
                    'commande' => $commande,
                    'form' => $form,
                ]
            );
        }

        $form->handleRequest($request);""",
    "Restauration de brouillon (Commandes::new)",
)

appliquer(
    CTRL_COMMANDE,
    """                $entityManager->flush();

                $this->addFlash(
                    'success',
                    sprintf(
                        'La commande %s a été enregistrée avec succès.',
                        $commande->getNumero()
                    )
                );""",
    """                $entityManager->flush();

                $request->getSession()->remove('brouillon_commande');

                $this->addFlash(
                    'success',
                    sprintf(
                        'La commande %s a été enregistrée avec succès.',
                        $commande->getNumero()
                    )
                );""",
    "Suppression du brouillon après enregistrement (Commandes)",
)


# ==================================================================
# 2) src/Controller/DevisController.php
# ==================================================================
CTRL_DEVIS = "src/Controller/DevisController.php"

appliquer(
    CTRL_DEVIS,
    """        $devi = new Devis();

        $form = $this->createForm(DevisType::class, $devi);
        $form->handleRequest($request);""",
    """        $devi = new Devis();

        $form = $this->createForm(DevisType::class, $devi);

        /*
     * ============================================================
     * RESTAURATION D'UN BROUILLON
     * ============================================================
     *
     * Pré-remplit le formulaire à partir d'une saisie sauvegardée
     * automatiquement en session (voir BrouillonSaisieController),
     * sans jamais déclencher l'enregistrement : on affiche juste le
     * formulaire pré-rempli, l'agent doit re-soumettre lui-même.
     */
        if (
            $request->isMethod('GET')
            && $request->query->get('restaurer') === '1'
        ) {
            $brouillon = $request->getSession()->get('brouillon_devis');

            if (is_array($brouillon) && !empty($brouillon['champs'])) {
                $form->submit($brouillon['champs'], false);
            }

            return $this->render('devis/new.html.twig', [
                'devi' => $devi,
                'form' => $form,
            ]);
        }

        $form->handleRequest($request);""",
    "Restauration de brouillon (Devis::new)",
)

appliquer(
    CTRL_DEVIS,
    """$this->initialiserTokenAuthenticiteDevis(
    $devi
);
            $entityManager->flush();

            $this->addFlash(""",
    """$this->initialiserTokenAuthenticiteDevis(
    $devi
);
            $entityManager->flush();

            $request->getSession()->remove('brouillon_devis');

            $this->addFlash(""",
    "Suppression du brouillon après enregistrement (Devis)",
)


# ==================================================================
# 3) templates/commandes/_form.html.twig
# ==================================================================
TPL_COMMANDE = "templates/commandes/_form.html.twig"

appliquer(
    TPL_COMMANDE,
    """        'data-upload-supprimer-url':
            modeleUrlSuppression
    }
}) }}""",
    """        'data-upload-supprimer-url':
            modeleUrlSuppression,

        'data-brouillon-nouvelle':
            commande.id is null ? '1' : '0',

        'data-brouillon-csrf':
            csrf_token('brouillon-commande'),

        'data-brouillon-enregistrer-url':
            path('app_brouillon_enregistrer', {type: 'commande'}),

        'data-brouillon-verifier-url':
            path('app_brouillon_verifier', {type: 'commande'})
    }
}) }}""",
    "Attributs data-brouillon-* (Commande)",
)

appliquer(
    TPL_COMMANDE,
    """initialiserSelect2(form);


afficherProfilClient();


rafraichirDetails();

}""",
    """initialiserSelect2(form);


afficherProfilClient();


rafraichirDetails();


initialiserBrouillon();

}


/*
 * ====================================================
 * BROUILLON (sauvegarde automatique en session)
 * ====================================================
 *
 * Uniquement pour une commande "nouvelle" (pas encore enregistrée) :
 * la saisie est sauvegardée automatiquement en session cote serveur
 * pendant que l'agent la remplit, pour pouvoir la restaurer si la
 * page se ferme ou plante avant l'enregistrement definitif.
 */
function initialiserBrouillon() {

if (form.dataset.brouillonNouvelle !== '1') {
return;
}

const brouillonEnregistrerUrl = form.dataset.brouillonEnregistrerUrl;
const brouillonVerifierUrl = form.dataset.brouillonVerifierUrl;
const brouillonCsrf = form.dataset.brouillonCsrf;

if (! brouillonEnregistrerUrl || ! brouillonCsrf) {
return;
}

function serialiserFormulaireBrouillon() {
const donnees = new FormData(form);
const params = new URLSearchParams();

for (const paire of donnees.entries()) {
const valeur = paire[1];

/*
 * Les fichiers ont deja leur propre mecanisme de
 * persistance (upload par morceaux + jeton) : impossible
 * et inutile de les remettre dans un brouillon.
 */
if (valeur instanceof File) {
continue;
}

params.append(paire[0], valeur);
}

return params;
}

function sauvegarderBrouillon() {
fetch(brouillonEnregistrerUrl, {
method: 'POST',
headers: {
'Content-Type': 'application/x-www-form-urlencoded',
'X-CSRF-TOKEN': brouillonCsrf
},
body: serialiserFormulaireBrouillon().toString()
}).catch(function (erreur) {
console.error(erreur);
});
}

let minuteurBrouillon = null;

form.addEventListener('input', function () {
if (minuteurBrouillon) {
clearTimeout(minuteurBrouillon);
}

minuteurBrouillon = setTimeout(sauvegarderBrouillon, 4000);
});

setInterval(sauvegarderBrouillon, 60000);

/*
 * Propose la restauration au chargement, sauf si on vient
 * justement de restaurer (evite de reproposer en boucle).
 */
if (
window.location.search.indexOf('restaurer=1') === -1
&& brouillonVerifierUrl
) {
fetch(brouillonVerifierUrl)
.then(function (reponse) {
return reponse.json();
})
.then(function (donnees) {
if (! donnees.existe || typeof window.Swal === 'undefined') {
return;
}

window.Swal.fire({
icon: 'question',
title: 'Saisie non terminée trouvée',
text: 'Une saisie de commande non enregistrée a été trouvée. Voulez-vous la restaurer ?',
showCancelButton: true,
confirmButtonText: 'Restaurer',
cancelButtonText: 'Ignorer'
}).then(function (resultat) {
if (resultat.isConfirmed) {
const url = new URL(window.location.href);

url.searchParams.set('restaurer', '1');

window.location.href = url.toString();
}
});
})
.catch(function (erreur) {
console.error(erreur);
});
}
}""",
    "Fonction initialiserBrouillon() (Commande)",
)


# ==================================================================
# 4) templates/devis/_form.html.twig
# ==================================================================
TPL_DEVIS = "templates/devis/_form.html.twig"

appliquer(
    TPL_DEVIS,
    """{{ form_start(form, {
    attr: {
        id: 'devis-form'
    }
}) }}""",
    """{{ form_start(form, {
    attr: {
        id: 'devis-form',

        'data-brouillon-nouvelle':
            form.vars.data.id is null ? '1' : '0',

        'data-brouillon-csrf':
            csrf_token('brouillon-devis'),

        'data-brouillon-enregistrer-url':
            path('app_brouillon_enregistrer', {type: 'devis'}),

        'data-brouillon-verifier-url':
            path('app_brouillon_verifier', {type: 'devis'})
    }
}) }}""",
    "Attributs data-brouillon-* (Devis)",
)

appliquer(
    TPL_DEVIS,
    """rafraichirDetails();


console.log('✅ Initialisation Devis terminée');

});
</script>""",
    """rafraichirDetails();


initialiserBrouillon();


console.log('✅ Initialisation Devis terminée');

});


/*
 * ====================================================
 * BROUILLON (sauvegarde automatique en session)
 * ====================================================
 *
 * Uniquement pour un devis "nouveau" (pas encore enregistré) : la
 * saisie est sauvegardée automatiquement en session cote serveur
 * pendant que l'agent la remplit, pour pouvoir la restaurer si la
 * page se ferme ou plante avant l'enregistrement definitif.
 */
function initialiserBrouillon() {

const form = document.getElementById('devis-form');

if (! form || form.dataset.brouillonNouvelle !== '1') {
return;
}

const brouillonEnregistrerUrl = form.dataset.brouillonEnregistrerUrl;
const brouillonVerifierUrl = form.dataset.brouillonVerifierUrl;
const brouillonCsrf = form.dataset.brouillonCsrf;

if (! brouillonEnregistrerUrl || ! brouillonCsrf) {
return;
}

function serialiserFormulaireBrouillon() {
const donnees = new FormData(form);
const params = new URLSearchParams();

for (const paire of donnees.entries()) {
const valeur = paire[1];

if (valeur instanceof File) {
continue;
}

params.append(paire[0], valeur);
}

return params;
}

function sauvegarderBrouillon() {
fetch(brouillonEnregistrerUrl, {
method: 'POST',
headers: {
'Content-Type': 'application/x-www-form-urlencoded',
'X-CSRF-TOKEN': brouillonCsrf
},
body: serialiserFormulaireBrouillon().toString()
}).catch(function (erreur) {
console.error(erreur);
});
}

let minuteurBrouillon = null;

form.addEventListener('input', function () {
if (minuteurBrouillon) {
clearTimeout(minuteurBrouillon);
}

minuteurBrouillon = setTimeout(sauvegarderBrouillon, 4000);
});

setInterval(sauvegarderBrouillon, 60000);

if (
window.location.search.indexOf('restaurer=1') === -1
&& brouillonVerifierUrl
) {
fetch(brouillonVerifierUrl)
.then(function (reponse) {
return reponse.json();
})
.then(function (donnees) {
if (! donnees.existe || typeof window.Swal === 'undefined') {
return;
}

window.Swal.fire({
icon: 'question',
title: 'Saisie non terminée trouvée',
text: 'Une saisie de devis non enregistrée a été trouvée. Voulez-vous la restaurer ?',
showCancelButton: true,
confirmButtonText: 'Restaurer',
cancelButtonText: 'Ignorer'
}).then(function (resultat) {
if (resultat.isConfirmed) {
const url = new URL(window.location.href);

url.searchParams.set('restaurer', '1');

window.location.href = url.toString();
}
});
})
.catch(function (erreur) {
console.error(erreur);
});
}
}
</script>""",
    "Fonction initialiserBrouillon() (Devis)",
)

print("\nTerminé.")
print("N'oublie pas de copier aussi src/Controller/BrouillonSaisieController.php")
print("(livré séparément) dans src/Controller/ — aucune migration n'est nécessaire.")
