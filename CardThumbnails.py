from IdolDatabase import *
from PIL import Image
import requests
import os
from colorama import Fore, Style
from collections import namedtuple

from IdolDatabase.Config import Config
from PageRenderer import get_file_modifyhash

AtlasMetadata = namedtuple('AtlasMetadata', 'group rarity atlas_plane coordinates')

def chunked(seq, size):
	for x in range(0, len(seq), size):
		yield seq[x:x+size]

class CardThumbnails():
	ATLAS_METADATA_FILE = "atlas_metadata.json"
	
	def __init__(self, client, output_directory):
		self.client = client
		self.output_directory = output_directory
		self.metadata_load_success = self.load_atlas_metadata()
	
	def metadata_loaded_successfully(self):
		return self.metadata_load_success
	
	def load_atlas_metadata(self):
		self.atlas_metadata = {}
		if os.path.exists(CardThumbnails.ATLAS_METADATA_FILE):
			try:
				with open(CardThumbnails.ATLAS_METADATA_FILE, "r") as f:
					metadata = json.load(f)
				
				for ordinal, data in metadata.items():
					self.atlas_metadata[int(ordinal)] = AtlasMetadata(Group(data[0]), Rarity(data[1]), data[2], data[3])
				
				return True
			except:
				self.atlas_metadata = {}
		return False
		
	def save_atlas_metadata(self):
		if not isinstance(self.atlas_metadata, dict):
			print(f'    {Fore.RED}{Style.BRIGHT}Atlas metadata not a dict!{Style.RESET_ALL}')
			return False
			
		def json_serialize(obj):
		    if isinstance(obj, (Group, Rarity)):
		        return obj.value
		    raise TypeError(f"Type {type(obj)} not serializable")
			
		with open(CardThumbnails.ATLAS_METADATA_FILE, "w", encoding="utf8") as output_file:
			json.dump(self.atlas_metadata, output_file, default=json_serialize)
			
		print(f'    {Fore.BLUE}{Style.BRIGHT}Saved atlas metadata   {Fore.WHITE}: {CardThumbnails.ATLAS_METADATA_FILE}{Style.RESET_ALL}')
		return True
		
		
	def make_random_string(self):
		hashvalue = hash(datetime.now()) % 16711425
		return f"{hashvalue:06x}"
	
	
	def download_file(self, url, target_path):
		r = requests.get(url, headers={
			'User-Agent' : Config.USER_AGENT,
		})
		if r.status_code == 200:
			with open(target_path, "wb") as f:
				f.write(r.content)
				f.close()
			return True
			
		print(f"{Fore.RED}Return code {r.status_code}, failed to download resource: {url}{Style.RESET_ALL}")
		return False
				
				
	def download_thumbnails(self):
		print(f"{Fore.BLUE}{Style.BRIGHT}Checking new thumbnails...{Style.RESET_ALL}")
		
		has_new_thumbnails = False
		
		cards = self.client.get_all_idols(with_json=True)
		for card in cards:
			normal_path = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_normal.png"
			if not os.path.exists(normal_path):
				print(f"  {Fore.YELLOW}{Style.BRIGHT}Downloading:   {Fore.WHITE}{normal_path}{Style.RESET_ALL}", end='')
				if self.download_file(card.data["normal_appearance"]["thumbnail_asset_path"], normal_path):
					print(f" {Fore.GREEN}{Style.BRIGHT}OK{Style.RESET_ALL}")
					has_new_thumbnails = True
				else:
					print(f" {Fore.RED}{Style.BRIGHT}FAIL!{Style.RESET_ALL}")
			
			idolized_path = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_idolized.png"
			if not os.path.exists(idolized_path):
				print(f"  {Fore.YELLOW}{Style.BRIGHT}Downloading:   {Fore.WHITE}{idolized_path}{Style.RESET_ALL}", end='')
				if self.download_file(card.data["idolized_appearance"]["thumbnail_asset_path"], idolized_path):
					print(f" {Fore.GREEN}{Style.BRIGHT}OK{Style.RESET_ALL}")
					has_new_thumbnails = True
				else:
					print(f" {Fore.RED}{Style.BRIGHT}FAIL!{Style.RESET_ALL}")
		
		if has_new_thumbnails:
			print(f"  {Fore.MAGENTA}{Style.BRIGHT}New thumbnails downloaded, remaking atlas is required.{Style.RESET_ALL}")
		else:
			print(f"  {Fore.BLACK}{Style.BRIGHT}No new thumbnails downloaded.{Style.RESET_ALL}")
		print()
		return has_new_thumbnails
	
	
	def get_atlas_plane(self, ordinal):
		try:
			assert(len(self.atlas_metadata) > 0)
			return self.atlas_metadata[ordinal].atlas_plane
		except KeyError:
			pass
		return 'error'
		
	
	def make_atlas(self):
		print(f"{Fore.GREEN}{Style.BRIGHT}Compiling thumbnail atlas planes...")
		
		self.atlas_metadata = {}
		atlas_identifiers = []
		
		size = 80
		thumbnail_size = (size, size)
		missing_icon = Image.open("thumbnails/missing_icon.png")
		missing_icon.thumbnail(thumbnail_size)
		
		rarities = [Rarity.SR, Rarity.UR]
		
		for rarity in rarities:
			for group in Group:
				print(f"  {Fore.YELLOW}{Style.BRIGHT}Processing atlas   {Fore.RED}{group.name} {rarity.name}...{Style.RESET_ALL}")
				
				num_members = len(Idols.by_group[group])
				
				cards = self.client.get_idols_by_group(group, rarity)
				cards_per_girl = defaultdict(list)
				for card in cards:
					cards_per_girl[card.member_id].append(card)
				
				num_rotations = 0
				for member_id, cards in cards_per_girl.items():
					num_rotations = max(num_rotations, len(cards))
				
				max_rotations_per_plane = 8
				num_atlas_planes = math.ceil(num_rotations / max_rotations_per_plane)
				
				# Slice card lists to separate planes
				cards_per_plane = [{} for x in range(0, num_atlas_planes)]
				for member_id, cards in cards_per_girl.items():
					for atlas_plane, plane_cards in enumerate(chunked(cards, max_rotations_per_plane)):
						cards_per_plane[atlas_plane][member_id] = plane_cards
					
				num_rotations_remaining = num_rotations
				for atlas_plane in range(0, num_atlas_planes):
					num_rotations_on_plane = min(num_rotations_remaining, max_rotations_per_plane)
					
					image_size     = (thumbnail_size[0] * num_members, thumbnail_size[1] * (num_rotations_on_plane + 1))
					atlas_normal   = Image.new('RGB', image_size, (0, 0, 0,))
					atlas_idolized = Image.new('RGB', image_size, (0, 0, 0,))
					
					atlas_normal.paste(missing_icon, (0, 0))
					atlas_idolized.paste(missing_icon, (0, 0))
					
					for column_index, ordered_member_id in enumerate(Idols.member_order_by_group[group]):
						# Skip if a member has no card thumbnails for this plane
						if ordered_member_id not in cards_per_plane[atlas_plane]:
							continue
						
						for row_index, card in enumerate(cards_per_plane[atlas_plane][ordered_member_id]):
							target_coordinates = (thumbnail_size[0] * column_index, thumbnail_size[1] * (row_index + 1))
							
							self.atlas_metadata[card.ordinal] = AtlasMetadata(group, rarity, atlas_plane, target_coordinates)
							
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
					
					atlas_identifier = f"atlas_{group.value}_{rarity.value}_{atlas_plane}"
					
					atlas_normal_path = os.path.join(self.output_directory, f'img/thumbnails/{atlas_identifier}_normal.png').replace('\\', '/')
					atlas_normal.save(atlas_normal_path, 'PNG')
					print(f'    {Fore.BLUE}{Style.BRIGHT}Saved normal atlas   (plane {atlas_plane + 1}/{num_atlas_planes})  {Fore.WHITE}: {atlas_normal_path}{Style.RESET_ALL}')
					
					atlas_idolized_path = os.path.join(self.output_directory, f'img/thumbnails/{atlas_identifier}_idolized.png').replace('\\', '/')
					atlas_idolized.save(atlas_idolized_path, 'PNG')
					print(f'    {Fore.BLUE}{Style.BRIGHT}Saved idolized atlas (plane {atlas_plane + 1}/{num_atlas_planes})  {Fore.WHITE}: {atlas_idolized_path}{Style.RESET_ALL}')
					
					filehashes = (
						get_file_modifyhash(atlas_normal_path),
						get_file_modifyhash(atlas_idolized_path),
					)
					atlas_identifiers.append((group, rarity, atlas_plane, filehashes))
					
					num_rotations_remaining -= max_rotations_per_plane
		
		print(f"{Fore.YELLOW}{Style.BRIGHT}Writing atlas css...{Style.RESET_ALL} ", end='')
		
		atlas_css = []
		for group, rarity, atlas_plane, (hash_normal, hash_idolized) in atlas_identifiers:
			atlas_identifier = f"atlas_{group.value}_{rarity.value}_{atlas_plane}"
			atlas_css.append(f"                         .card-thumbnail.group-{group.value}-{rarity.value}-{atlas_plane} {{ background: url('/img/thumbnails/{atlas_identifier}_normal.{hash_normal}.png') no-repeat; }}")
			atlas_css.append(f".use-idolized-thumbnails .card-thumbnail.group-{group.value}-{rarity.value}-{atlas_plane} {{ background: url('/img/thumbnails/{atlas_identifier}_idolized.{hash_idolized}.png') no-repeat; }}")
		
		for ordinal, (group, rarity, atlas_plane, coordinates) in self.atlas_metadata.items():
			atlas_css.append(f".card-thumbnail.card-{ordinal} {{ background-position: {-coordinates[0]}px {-coordinates[1]}px !important; }}")
			
		for group, rarity, atlas_plane, (hash_normal, hash_idolized) in atlas_identifiers:
			atlas_css.append(f"                         .card-thumbnail.group-{group.value}-{rarity.value}-error         {{ background: url('/img/missing_icon.png') no-repeat 0px 0px !important; }}")
			atlas_css.append(f".use-idolized-thumbnails .card-thumbnail.group-{group.value}-{rarity.value}-error         {{ background: url('/img/missing_icon.png') no-repeat 0px 0px !important; }}")
		
		with open("assets/css/atlas.css", "w", encoding="utf8") as output_file:
			for line in atlas_css:
				output_file.write(line + "\n")
			
		self.save_atlas_metadata()
			
		print(f"{Fore.GREEN}{Style.BRIGHT}Done!  {Fore.MAGENTA}{Style.BRIGHT}Atlas processing complete!{Style.RESET_ALL}")
		print()
	
