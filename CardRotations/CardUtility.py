
from IdolDatabase import *
from Common import Utility
import json

class CardUtility:
	@staticmethod
	def get_card_source_label(card):
		if card.from_event_gacha():
			return 'Event Gacha'
		return card.source.display_name
		
	@staticmethod
	def serialize_card(card):
		data = {
			'm' : card.member_id.value,
			'd' : [ card.ordinal, card.rarity.value, card.attribute.value, card.type.value ],
			't' : [ card.get_card_name(False), card.get_card_name(True) ],
			's' : CardUtility.get_card_source_label(card),
			'r' : [ int(card.release_date[Locale.JP].timestamp()) ],
		}
		
		if card.release_date[Locale.JP] != card.release_date[Locale.WW]:
			data['r'].append( int(card.release_date[Locale.WW].timestamp()) )
		
		if card.event.title:
			data['e'] = card.event.title
			
		return data
	
	@staticmethod
	def base64encode_json(data):
		serialized = json.dumps(data, separators=(',', ':'))
		return base64.b64encode(serialized.encode('utf-8')).decode('utf-8')
		
	@staticmethod
	def card_to_base64(card):
		return CardUtility.base64encode_json(CardUtility.serialize_card(card))
