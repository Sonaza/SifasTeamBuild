idols = [
	1, 2, 3, 4, 5, 6, 7, 8, 9,                                   # Muse
	101, 102, 103, 104, 105, 106, 107, 108, 109,                 # Aqours
	201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212,  # Nijigasaki
	301, 302, 303, 304, 305,                                     # Liella
]
idol_colors = list(zip(idols, [
	'f39801', '1eb8ec', 'abadac', '2c72b7', 'fef102', 'e93421', '925da3', '23ac3a', 'ec6f9b', 
	'f28100', 'f39c95', '63c0ad', 'e70014', '67aadf', '9f9f9f', 'fee202', '6458a4', 'ee6da6', 
	'f0939e', 'f7f064', '81c6ef', '034099', 'eb6001', 'ba8ec1', 'da363f', '6cbd61', 'a8aaa9', '2c9e7e', 'd6d5ca', 'f8c8c4', 
	'ff7f27', 'a0fff9', 'ff6e90', '74f466', '0000a0', 
]))

attributes = [1, 2, 3, 4, 5, 6]
attribute_colors = list(zip(attributes, ['dd4aa5', '38a75c', '0099ee', 'db3e3e', 'edba3c', '85519c']))

types = [1, 2, 3, 4]
type_colors = list(zip(types, ['cf413f','268fd0','3fa45d','e3b643']))

rarities = [10, 20, 30]

icon_sizes = [32, 48, 64, 128]

def darken(hex, m):
	r = int(int(hex[0:2], 16) * m)
	g = int(int(hex[2:4], 16) * m)
	b = int(int(hex[4:6], 16) * m)
	return f'{r:02x}{g:02x}{b:02x}'

f = open("../output/css/idols.css", "w", encoding="utf-8")

for size in icon_sizes:
	for attribute in attributes:
		line = f".icon-{size}.attribute-{attribute} {{ background-image: url('/img/icons/{size}/attribute-{attribute}.png') !important; }}"
		f.write(line + "\n")
		
for attribute, color in attribute_colors:
	line = f".attribute-{attribute}.attribute-bg-color      {{ background-color: #{color} !important; }}"
	f.write(line + "\n")
	line = f".attribute-{attribute}.attribute-bg-color-dim  {{ background-color: #{darken(color, 0.7)} !important; }}"
	f.write(line + "\n")
	line = f".attribute-{attribute}.attribute-bg-color-dark {{ background-color: #{darken(color, 0.4)} !important; }}"
	f.write(line + "\n")
	
	line = f"tr:hover .attribute-{attribute}.attribute-bg-color-dim  {{ background-color: #{darken(color, 0.85)} !important; }}"
	f.write(line + "\n")

for size in icon_sizes:
	for type in types:
		line = f".icon-{size}.type-{type} {{ background-image: url('/img/icons/{size}/type-{type}.png') !important; }}"
		f.write(line + "\n")
		
for type, color in type_colors:
	line = f".type-{type}.type-bg-color      {{ background-color: #{color} !important; }}"
	f.write(line + "\n")
	line = f".type-{type}.type-bg-color-dim  {{ background-color: #{darken(color, 0.7)} !important; }}"
	f.write(line + "\n")
	line = f".type-{type}.type-bg-color-dark {{ background-color: #{darken(color, 0.4)} !important; }}"
	f.write(line + "\n")
	
	line = f"tr:hover .type-{type}.type-bg-color-dim  {{ background-color: #{darken(color, 0.85)} !important; }}"
	f.write(line + "\n")

for size in icon_sizes:
	for rarity in rarities:
		line = f".icon-{size}.rarity-{rarity} {{ background-image: url('/img/icons/{size}/rarity-{rarity}.png') !important; }}"
		f.write(line + "\n")

f.write("\n")

for size in icon_sizes:
	for idol in idols:
		line = f".idol-{idol:<3} .idol-icon-{size}        {{ background-image: url('/img/icons/{size}/icon-{idol}.png') !important; }}"
		f.write(line + "\n")
	f.write("\n")
	
for size in icon_sizes:
	for idol in idols:
		line = f".idol-{idol:<3} .idol-icon-{size}-border {{ background-image: url('/img/icons/{size}/icon-{idol}-border.png') !important; }}"
		f.write(line + "\n")
		
	f.write("\n")

for idol, color in idol_colors:
	line = f".idol-{idol:<3} .idol-bg-color      {{ background-color: #{color} !important; }}"
	f.write(line + "\n")
f.write("\n")

for idol, color in idol_colors:
	line = f".idol-{idol:<3} .idol-bg-color-dim  {{ background-color: #{darken(color, 0.7)} !important; }}"
	f.write(line + "\n")
f.write("\n")

for idol, color in idol_colors:
	line = f".idol-{idol:<3} .idol-bg-color-dark {{ background-color: #{darken(color, 0.4)} !important; }}"
	f.write(line + "\n")
f.write("\n")

for idol, color in idol_colors:
	line = f".idol-{idol:<3} .idol-bg-glow       {{ box-shadow: inset 0 0 4px 2px #{color}77 !important; }}"
	f.write(line + "\n")
f.write("\n")

for idol, color in idol_colors:
	line = f".idol-{idol:<3} .idol-bg-glow-faint {{ box-shadow: inset 0 0 4px 2px #{color}33 !important; }}"
	f.write(line + "\n")

for idol, color in idol_colors:
	line = f".idol-{idol:<3} .idol-bg-glow-border {{ box-shadow: inset 0 0 1px 1px #{color}44 !important; }}"
	f.write(line + "\n")
