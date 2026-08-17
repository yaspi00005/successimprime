import re

path = "templates/base.html.twig"

with open(path, encoding="utf-8") as f:
    content = f.read()

start_marker = "<a href=\"{{ path('app_reclamation_index') }}\""

count = content.count(start_marker)
assert count == 1, f"attendu 1 occurrence de l'ancien lien, trouvé {count}"

start = content.index(start_marker)
end = content.index("</a>", start) + len("</a>")

removed = content[start:end]
assert "Réclamations" in removed, "le bloc retiré ne contient pas 'Réclamations', arrêt par sécurité"

new_content = content[:start] + content[end:]

# Nettoie un éventuel excès de lignes vides laissé par la suppression,
# uniquement dans une petite fenêtre autour du point de suppression.
window_start = max(0, start - 20)
window_end = min(len(new_content), start + 200)

before = new_content[:window_start]
window = new_content[window_start:window_end]
after = new_content[window_end:]

window_fixed = re.sub(r"\n{4,}", "\n\n\n", window)

final_content = before + window_fixed + after

with open(path, "w", encoding="utf-8") as f:
    f.write(final_content)

print("OK - ancien lien Réclamations retiré du panneau Commercial")
