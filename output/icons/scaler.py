import os
from PIL import Image
from glob import glob

icons = glob("large/*.png")

for icon in icons:
	im = Image.open(icon)
	
	im.thumbnail((128, 128))
	
	target_path = f'128/{os.path.basename(icon)}'
	
	print("Saving", target_path)
	im.save(target_path)
	
