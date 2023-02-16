import Config
from IdolDatabase import *

from CardRotations import GeneratorBase
from ..Utility import Utility

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from collections import defaultdict, namedtuple

class AttributeTypeArrayGenerator(GeneratorBase):
	def __init__(self, parent):
		super().__init__(parent)
	
	used_templates = ["attribute_type_array.html"]

	def generate_and_render(self):
		idol_arrays = [(group, *self.get_attribute_type_array(group)) for group in Group]
		for data in idol_arrays:
			self.render_and_save("attribute_type_array.html", f"pages/idol_arrays_{data[0].tag}.html", {
				'idol_arrays'        : [ data ],
			}, minify=not self.args.dev)
		return True
		
	def get_attribute_type_array(self, group : Group):
		cards_per_girl = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
		
		for member in Idols.by_group[group]:
			for type in Type:
				if type == Type.Unset: continue
				for attribute in Attribute:
					if attribute == Attribute.Unset: continue
					cards_per_girl[member][type][attribute] = list()
			
		num_pages = 0
		for idol in self.client.get_idols_by_group(group, Rarity.UR):
			cards_per_girl[idol.member_id][idol.type][idol.attribute].append(idol)
			num_pages = max(num_pages, len(cards_per_girl[idol.member_id][idol.type][idol.attribute]))
		
		order = Idols.member_order_by_group[group]
		if group == Group.Nijigasaki:
			order = [
				Member.Rina,     Member.Kasumi,  Member.Shizuku, 
				Member.Ayumu,    Member.Setsuna, Member.Ai,      
				Member.Emma,     Member.Kanata,  Member.Karin,   
				Member.Shioriko, Member.Lanzhu,  Member.Mia,
			]
		
		arrays_sorted = Utility.sort_by_key_order(cards_per_girl, order)
		return (num_pages, arrays_sorted)
	
