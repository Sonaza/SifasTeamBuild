import Config
from IdolDatabase import *

from CardRotations import GeneratorBase
from Common import Utility

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
		
class BannersGenerator(GeneratorBase):
	def __init__(self, parent):
		super().__init__(parent)
	
	used_templates = ["banners.html", "banners_row.html"]
	
	def generate_and_render(self):
		banners_with_cards = self.get_banners_with_cards()
		for banner_index, (banner_id, banner_data) in enumerate(banners_with_cards.items()):
			self.render_and_save("banners_row.html", f"pages/deferred/banner_{banner_id}.html", {
				'banner_id'        : banner_id,
				'banner_data'      : banner_data,
				'banner_row_index' : banner_index + 1,
			}, minify_html=not self.args.dev)
			
		self.render_and_save("banners.html", "pages/banners.html", {
			'banners_with_cards' : reversed(list(banners_with_cards.items())),
		}, minify_html=not self.args.dev)
		
		return True
	
	def get_banners_with_cards(self):
		banners = self.client.get_banners_with_cards()
		
		banner_title_overrides = dict([
			(21, "Initial SR Shioriko (Nijigasaki Festival)"),
			(48, "Initial SR Mia and Lanzhu"),
		])
		
		for banner_id, data in banners.items():
			featured_members = []
			num_urs = sum([1 for card in data['cards'] if card.rarity == Rarity.UR])
			
			data['idols'] = []
			for idol in data['cards']:
				data['idols'].append(f"has-idol-{idol.member_id.value}")
				
				if num_urs == 0 or idol.rarity == Rarity.UR:
					featured_members.append(idol.member_id.first_name)
				
			data['idols'] = ' '.join(data['idols'])
			
			featured_str = Utility.concat(featured_members, separator=', ', last_separator=' and ')
			
			data['banner']['ordinal'] = ""
			
			if banner_id in banner_title_overrides:
				data['banner']['title'] = banner_title_overrides[banner_id]
			
			else:
				data['banner']['title'] = f"{data['banner']['type'].name} {featured_str}"
				
				if data['banner']['type'] != BannerType.Spotlight:
					data['banner']['ordinal'] = Utility.ordinalize(data['index'] + 1)
				
			data['banner']['title_with_ordinal'] = f"{data['banner']['ordinal']} {data['banner']['title']}".strip()
					
		
		return banners
	
	
