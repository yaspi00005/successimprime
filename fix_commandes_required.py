path = "templates/commandes/_form.html.twig"

with open(path, encoding="utf-8") as f:
    content = f.read()

old = """if (configuration) {
configuration.required = produit && valeurModeConfiguration(detail) === 'automatique';
}


if (produit) {"""

new = """if (configuration) {
configuration.required = produit && valeurModeConfiguration(detail) === 'automatique';
}

detail.querySelectorAll('[name$="[modeConfiguration]"]').forEach(function (radio) {
radio.required = produit;
});


if (produit) {"""

count = content.count(old)
assert count == 1, f"attendu 1 occurrence, trouvé {count}"

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("OK - required corrige sur modeConfiguration")