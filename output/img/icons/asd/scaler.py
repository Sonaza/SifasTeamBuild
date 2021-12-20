import os
from PIL import Image
from glob import glob

# icons = glob("large/*.png")
icons = ['large/icon_107.png']

for size in [32, 48, 64, 128]:
	sizedir = f'{size}'
	if not os.path.exists(sizedir):
		try:
			os.mkdir(sizedir)
		except:
			pass
	
	for icon in icons:
		im = Image.open(icon)
		im = im.convert('RGBA')
		# print(im.format, im.size, im.mode)
		
		im.thumbnail((size, size), Image.BICUBIC)
		
		name, ext = os.path.splitext(os.path.basename(icon))
		target_path = f'{size}/{name}_border{ext}'
		
		# print(f".grid-icon .{os.path.basename(icon).split('.')[0]} {{ background-image: url('icons/32/{os.path.basename(icon)}'); }}")
		
		print("Saving", target_path)
		im.save(target_path)
	