import Config
from IdolDatabase import *

from CardRotations import GeneratorBase
from ..Utility import Utility

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
		
class EventHistoryGenerator(GeneratorBase):
	def __init__(self, parent):
		super().__init__(parent)
	
	used_templates = ["event_history.html", "event_history_row.html"]
	
	def generate_and_render(self):
		events_with_cards, zero_feature_members = self.get_events_with_cards()
		for event_index, (event_id, event_data) in enumerate(events_with_cards.items()):
			self.render_and_save("event_history_row.html", f"pages/deferred/event_history_{event_id}.html", {
				'event_id'        : event_id,
				'event_data'      : event_data,
				'event_row_index' : event_index + 1,
			}, minify=not self.args.dev)
		
		self.render_and_save("event_history.html", "pages/event_history.html", {
			'events_with_cards'    : events_with_cards,
			'zero_feature_members' : zero_feature_members,
		}, minify=not self.args.dev)
		
		return True

	def get_events_with_cards(self):
		events = self.client.get_events_with_cards()
		features = self.client.get_event_features_per_member()
		
		zero_feature_members = [member for member, num_features in features.items() if num_features == 0]
		
		sbl_reference_point = {
			'event_id' : 47,
			'date'     : datetime(year=2022, month=9, day=1),
		}
		today = datetime.today()
		while sbl_reference_point['date'].month != today.month or sbl_reference_point['date'].year != today.year:
			if (sbl_reference_point['event_id'] + 1) not in events:
				break

			sbl_reference_point['event_id'] += 1
			sbl_reference_point['date'] += relativedelta(months=1)
		
		events_per_month = 1
		diff_bonus = 0
		for event_id, data in events.items():
			# if event_id == 49:
			# 	events_per_month = 1
			# 	diff_bonus = 14
			
			data['idols'] = []
			data['idols'].append(f"featured-idol-{data['free'][0].member_id.value}")
			
			for idol in data['free'] + data['gacha']:
				data['idols'].append(f"has-idol-{idol.member_id.value}")
			data['idols'] = ' '.join(data['idols'])
			
			if event_id <= sbl_reference_point['event_id']:
				continue
			
			diff = ((event_id - sbl_reference_point['event_id']) - 1) // events_per_month + 1 - diff_bonus
			estimated_addition = sbl_reference_point['date'] + relativedelta(months=diff)
			data['sbl'] = estimated_addition.strftime('%b %Y')
		
		return events, zero_feature_members
	
