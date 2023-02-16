import os
from PIL import Image
from glob import glob

border = ""
# border = "-border"

icons = glob(f"large{border}/*.png")
# icons = ['large/icon_107.png']

for size in [16, 32, 48, 64, 128]:
# for size in [16]:
	sizedir = f'{size}'
	if not os.path.exists(sizedir):
		try:
			os.mkdir(sizedir)
		except:
			pass
	
	for icon in icons:
		name, ext = os.path.splitext(os.path.basename(icon))
		name = name.split('-')
		name = f"{name[0]}-{name[1]}"
		target_path = f'{size}/{name}{border}{ext}'
		
		if os.path.exists(target_path):
			continue
			
		im = Image.open(icon)
		im = im.convert('RGBA')
		# print(im.format, im.size, im.mode)
		
		im.thumbnail((size, size), Image.BICUBIC)
		
		# print(f".grid-icon .{os.path.basename(icon).split('.')[0]} {{ background-image: url('icons/32/{os.path.basename(icon)}'); }}")
		
		print("Saving", target_path)
		im.save(target_path)
	
