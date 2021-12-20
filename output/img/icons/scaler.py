import os
from PIL import Image
from glob import glob

icons = glob("large/*.png")

for size in [32, 48, 64, 128]:
	for icon in icons:
		im = Image.open(icon)
		im = im.convert('RGBA')
		print(im.format, im.size, im.mode)
		
		im.thumbnail((size, size), Image.BICUBIC)
		
		target_path = f'{size}/{os.path.basename(icon)}'
		
		# print(f".grid-icon .{os.path.basename(icon).split('.')[0]} {{ background-image: url('icons/32/{os.path.basename(icon)}'); }}")
		
		print("Saving", target_path)
		im.save(target_path)
	
