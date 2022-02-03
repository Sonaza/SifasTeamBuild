from IdolDatabase import *
from PIL import Image
import requests
import os

class CardThumbnails():
	def __init__(self, client, output_directory):
		self.client = client
		self.output_directory = output_directory
		
	def _make_random_string(self):
		hashvalue = hash(datetime.now()) % 16711425
		return f"{hashvalue:06x}"
	
	def _download_file(self, url, target_path):
		r = requests.get(url)
		if r.status_code == 200:
			with open(target_path, "wb") as f:
				f.write(r.content)
				f.close()
			return True
			
		print(f"Return code {r.status_code}, failed to download resource: {url}")
		return False
				
	def download_thumbnails(self):
		print("Checking new thumbnails...")
		
		has_new_thumbnails = False
		
		cards = self.client.get_all_idols(with_json=True)
		for card in cards:
			normal_path = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_normal.png"
			if not os.path.exists(normal_path):
				print("Downloading:", normal_path, end='')
				if self._download_file(card.data["normal_appearance"]["thumbnail_asset_path"], normal_path):
					print(" OK")
					has_new_thumbnails = True
				else:
					print(" FAIL!")
			
			idolized_path = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_idolized.png"
			if not os.path.exists(idolized_path):
				print("Downloading:", idolized_path, end='')
				if self._download_file(card.data["idolized_appearance"]["thumbnail_asset_path"], idolized_path):
					print(" OK")
					has_new_thumbnails = True
				else:
					print(" FAIL!")
		
		# return True
		return has_new_thumbnails
	
	def make_atlas(self):
		print("Making atlas...")
		
		atlas_by_ordinal = {}
		sizes = [80]
		rarities = [Rarity.SR, Rarity.UR]
		
		atlas_hash = self._make_random_string()
		
		for rarity in rarities:
			print(rarity.name)
			
			for group in Group:
				print(group.name)
				
				cards = self.client.get_idols_by_group(group, rarity)
				cards_per_girl = defaultdict(list)
				for card in cards:
					cards_per_girl[card.member_id].append(card)
				
				num_rotations = 0
				num_members = len(Idols.by_group[group])
				for member_id, cards in cards_per_girl.items():
					num_rotations = max(num_rotations, len(cards))
				
				for size in sizes:
					thumbnail_size = (size, size)
					image_size = (thumbnail_size[0] * num_members, thumbnail_size[1] * (num_rotations + 1))
					atlas_normal = Image.new('RGB', image_size, (0, 0, 0,))
					atlas_idolized = Image.new('RGB', image_size, (0, 0, 0,))
					
					missing_icon = Image.open("thumbnails/missing_icon.png")
					missing_icon.thumbnail(thumbnail_size)
					atlas_normal.paste(missing_icon, (0, 0))
					atlas_idolized.paste(missing_icon, (0, 0))
					
					for column_index, ordered_member_id in enumerate(Idols.member_order_by_group[group]):
						for row_index, card in enumerate(cards_per_girl[ordered_member_id]):
							target_coordinates = (thumbnail_size[0] * column_index, thumbnail_size[1] * (row_index + 1))
							
							atlas_by_ordinal[card.ordinal] = (group, rarity, 0, target_coordinates)
							
							normal = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_normal.png"
							im_normal = Image.open(normal)
							im_normal.thumbnail(thumbnail_size)
							atlas_normal.paste(im_normal, target_coordinates)
							
							idolized = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_idolized.png"
							im_idolized = Image.open(idolized)
							im_idolized.thumbnail(thumbnail_size)
							atlas_idolized.paste(im_idolized, target_coordinates)
							
							im_normal.close()
							im_idolized.close()
					
					atlas_normal_path = os.path.join(self.output_directory, f'img/thumbnails/atlas_{group.value}_{rarity.value}_0_normal.png')
					atlas_normal.save(atlas_normal_path, 'PNG')
					print(f'Saved {atlas_normal_path}')
					
					atlas_idolized_path = os.path.join(self.output_directory, f'img/thumbnails/atlas_{group.value}_{rarity.value}_0_idolized.png')
					atlas_idolized.save(atlas_idolized_path, 'PNG')
					print(f'Saved {atlas_idolized_path}')
					
				
		groups = []
		for rarity in rarities:
			for group in Group:
				groups.append(f"                         .card-thumbnail.group-{group.value}-{rarity.value} {{ background: url('/img/thumbnails/atlas_{group.value}_{rarity.value}_0_normal.{atlas_hash}.png') no-repeat; }}")
				groups.append(f".use-idolized-thumbnails .card-thumbnail.group-{group.value}-{rarity.value} {{ background: url('/img/thumbnails/atlas_{group.value}_{rarity.value}_0_idolized.{atlas_hash}.png') no-repeat; }}")
		
		atlas_css = os.path.join("assets/css/atlas.css")
		with open(atlas_css, "w", encoding="utf8") as f:
			print("Writing css... ")
			
			for line in groups:
				f.write(line + "\n")
			
			for ordinal, (group, rarity, atlas_index, coordinates) in atlas_by_ordinal.items():
				line = f".card-thumbnail.card-{ordinal} {{ background-position: {-coordinates[0]}px {-coordinates[1]}px !important; }}"
				f.write(line + "\n")
			
			f.close()
			
			print("Done")
