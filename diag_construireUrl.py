path = "templates/commandes/_form.html.twig"
content = open(path, encoding="utf-8").read()

old = """function construireUrlMorceauUpload(jeton, index) {
return uploadMorceauUrlModele
.replace('__JETON__', jeton)
.replace('__INDEX__', String(index));
}"""

idx = content.find("function construireUrlMorceauUpload")
print("count of exact old string:", content.count(old))
print("--- actual bytes around the function (repr) ---")
print(repr(content[idx-5:idx+300]))
