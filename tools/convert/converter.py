import os
from PIL import Image
from glob import glob

images = glob(f"*.png") + glob(f"*.jpg")

output_directory = "output"
if not os.path.exists(output_directory):
	try:
		os.mkdir(output_directory)
	except:
		pass

for filename in images:
	name, ext = os.path.splitext(os.path.basename(filename))
	target_path = f'{output_directory}/{name}.webp'
	
	# if os.path.exists(target_path):
	# 	continue
		
	im = Image.open(filename)
	im = im.convert('RGBA')
	
	print(f"Saving {target_path:<50} ", end='')
	
	original_size = os.path.getsize(filename)
	
	if original_size < 20 * 1024:
		im.save(target_path, "WEBP", lossless=True, quality=100)
	else:
		im.save(target_path, "WEBP", lossless=False, quality=70)
		
	new_size = os.path.getsize(target_path)
	
	print(f"  {original_size / 1024:>7.2f} KB   -> {new_size / 1024:>7.2f} KB   ({(new_size / original_size) * 100:0.1f}% of original)")
