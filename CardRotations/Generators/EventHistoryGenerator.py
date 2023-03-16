import Config
from IdolDatabase import *

from CardRotations import GeneratorBase
from Common import Utility

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
			}, minify_html=not self.args.dev)
		
		self.render_and_save("event_history.html", "pages/event_history.html", {
			'events_with_cards'    : reversed(list(events_with_cards.items())),
			'zero_feature_members' : zero_feature_members,
		}, minify_html=not self.args.dev)
		
		return True
	
	# ---------------------------------------------------------------
		
	def calculate_sbl_additions(self, events):
		addition_dates_output = {}
		# additions_per_month = 1
		
		reference_points_template = [
			(datetime(year=2022, month=9, day=1), [47]),
			(datetime(year=2023, month=4, day=1), Utility.tuple_range(54, 19)), # Events 54 to 72 are in a dump release
		]
		reference_points = {event_id: addition_date for addition_date, event_ids in reference_points_template for event_id in event_ids}
		
		today = datetime.today()
		
		first_event_id = next(iter(reference_points))
		for event_id, data in events.items():
			if event_id < first_event_id:
				continue
			
			if event_id in reference_points:
				current_addition_date = reference_points[event_id]
			else:
				current_addition_date += relativedelta(months=1)
			
			addition_dates_output[event_id] = current_addition_date
		
		return addition_dates_output

	# ---------------------------------------------------------------
	
	def get_events_with_cards(self):
		events = self.client.get_events_with_cards()
		features = self.client.get_event_features_per_member()
		
		zero_feature_members = [member for member, num_features in features.items() if num_features == 0]
		
		sbl_additions = self.calculate_sbl_additions(events)
		today = datetime.today()
		
		for event_id, data in events.items():
			data['idols'] = []
			data['idols'].append(f"featured-idol-{data['free'][0].member_id.value}")
			
			for idol in data['free'] + data['gacha']:
				data['idols'].append(f"has-idol-{idol.member_id.value}")
			data['idols'] = ' '.join(data['idols'])
			
			if event_id not in sbl_additions:
				continue
			
			estimated_addition = sbl_additions[event_id]
			if estimated_addition <= today:
				continue
			
			data['sbl'] = Utility.format_datestring(estimated_addition, with_day=False, with_year=True)
		
		return events, zero_feature_members
	
