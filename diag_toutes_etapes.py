path = "templates/commandes/_form.html.twig"
content = open(path, encoding="utf-8").read()

etapes = {
    "5_construireUrlSuppressionFichier": """function construireUrlMorceauUpload(jeton, index) {
return uploadMorceauUrlModele
.replace('__JETON__', jeton)
.replace('__INDEX__', String(index));
}""",
    "6_bouton_creerLigneUpload": """ligne.appendChild(apercu);
ligne.appendChild(infos);

return ligne;
}

function ajouterJetonFichier(detail, jeton) {
const champ = detail.querySelector('.js-jetons-fichiers');""",
    "7_retirerJeton_supprimerFichier": """champ.value = valeurs.join(',');
}

async function televerserFichier(detail, fichier, ligneUpload) {""",
    "8_ligneUpload_dataset_jeton": """const jeton = donneesInit.jeton;

for (let index = 0; index < nombreMorceaux; index++) {""",
    "9_binding_clic": """for (const fichier of fichiers) {

const ligne = creerLigneUpload(fichier);

zoneListe.appendChild(ligne);

await televerserFichier(detail, fichier, ligne);
}
});
}


function champDetail(detail, nom) {""",
}

for nom, old in etapes.items():
    trouve = content.count(old)
    print(f"{nom} : {trouve} occurrence(s)")

    if trouve == 0:
        # Cherche un fragment plus court pour localiser la zone réelle.
        premiere_ligne = old.split("\n")[0]
        idx = content.find(premiere_ligne)

        if idx == -1:
            print(f"   -> même la première ligne est introuvable : {premiere_ligne!r}")
        else:
            print(f"   -> contenu réel autour de cette zone :")
            print("   " + repr(content[idx:idx + len(old) + 60]))
    print()
