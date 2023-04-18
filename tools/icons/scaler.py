import os
from PIL import Image
from glob import glob

def mkdir(path):
	try:
		os.mkdir(path)
	except:
		pass

border = ""
# border = "-border"

categories = {
	'general' : [16, 32, 48, 64, 128],
	# 'yay'     : [64],
}

for directory, category_sizes in categories.items():
	icons = glob(os.path.join(directory, f"large{border}/*.png"))

	for size in category_sizes:
		sizedir = os.path.join(directory, str(size))
		
		mkdir(sizedir)
		
		for icon in icons:
			name, ext = os.path.splitext(os.path.basename(icon))
			name = name.split('-')
			name = f"{name[0]}-{name[1]}"
			target_path = f'{sizedir}/{name}{border}{ext}'.replace('\\', '/')
			
			if os.path.exists(target_path):
				continue
				
			im = Image.open(icon)
			im = im.convert('RGBA')
			# print(im.format, im.size, im.mode)
			
			im.thumbnail((size, size), Image.BICUBIC)
			
			# print(f".grid-icon .{os.path.basename(icon).split('.')[0]} {{ background-image: url('icons/32/{os.path.basename(icon)}'); }}")
			
			print("Saving", target_path)
			im.save(target_path)
		
