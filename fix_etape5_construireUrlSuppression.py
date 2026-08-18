path = "templates/commandes/_form.html.twig"

with open(path, encoding="utf-8") as f:
    content = f.read()

old = """function construireUrlMorceauUpload(jeton, index) {
return uploadMorceauUrlModele.replace('__JETON__', jeton).replace('__INDEX__', String(index));
}"""

new = """function construireUrlMorceauUpload(jeton, index) {
return uploadMorceauUrlModele.replace('__JETON__', jeton).replace('__INDEX__', String(index));
}

function construireUrlSuppressionFichier(jeton) {
return uploadSupprimerUrlModele.replace('__JETON__', jeton);
}"""

if new in content:
    print("Déjà présent - rien à faire.")
else:
    count = content.count(old)
    if count != 1:
        print(f"[ERREUR] {count} occurrence(s) trouvée(s) (1 attendue)")
    else:
        content = content.replace(old, new)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        print("OK - construireUrlSuppressionFichier() ajouté.")
