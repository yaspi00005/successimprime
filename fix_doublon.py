import re

path = "templates/devis/_form.html.twig"

with open(path, encoding="utf-8") as f:
    content = f.read()

# --- Bloc HTML ---
marker_info = content.index("INFORMATIONS DEVIS")
before_info = content[:marker_info]

occurrences = [m.start() for m in re.finditer("FACTURATION À UN TIERS", before_info)]
assert len(occurrences) == 2, f"attendu 2 occurrences HTML avant INFORMATIONS DEVIS, trouvé {len(occurrences)}"

comment_open = before_info.rfind("{#", 0, occurrences[1])
info_comment_open = content.rfind("{#", 0, marker_info)

new_content = content[:comment_open] + content[info_comment_open:]

# --- Bloc JS (recherche limitée à la zone <script>, pas tout le fichier) ---
script_pos = new_content.index("DOMContentLoaded")

m = re.search(r"\n[ \t]*INITIALISATION[ \t]*\n", new_content[script_pos:])
assert m is not None, "marqueur INITIALISATION (fin de fichier) introuvable"
marker_init = script_pos + m.start()

before_init = new_content[script_pos:marker_init]

occurrences_js = [mm.start() for mm in re.finditer("FACTURATION À UN TIERS", before_init)]
assert len(occurrences_js) == 2, f"attendu 2 occurrences JS avant INITIALISATION, trouvé {len(occurrences_js)}"

comment_open_js = script_pos + before_init.rfind("/*", 0, occurrences_js[1])
init_comment_open = new_content.rfind("/*", 0, marker_init)

final_content = new_content[:comment_open_js] + new_content[init_comment_open:]

with open(path, "w", encoding="utf-8") as f:
    f.write(final_content)

print("OK - doublon supprimé")