
from .Enums import *

NextEventOrder = {
	EventType.Exchange : EventType.Story,
	EventType.Story    : EventType.Exchange,
}

NextBannerOrder = {
	BannerType.Festival : BannerType.Party,
	BannerType.Party    : BannerType.Festival,
}

ApproximateStartDate = {
	BannerType.Festival : {
		1  : 30,
		2  : 27,
		3  : 25,
		4  : 29,
		5  : 30,
		6  : 28,
		7  : 30,
		8  : 30,
		9  : 25,
		10 : 30,
		11 : 29,
		12 : 30,
	},
	
	BannerType.Party : {
		1  : 14,
		2  : 14,
		3  : 14,
		4  : 14,
		5  : 14,
		6  : 14,
		7  : 14,
		8  : 14,
		9  : 14,
		10 : 14,
		11 : 14,
		12 : 14,
	},
	
	EventType.Exchange : {
		1  : 7,
		2  : 7,
		3  : 7,
		4  : 7,
		5  : 7,
		6  : 7,
		7  : 7,
		8  : 7,
		9  : 7,
		10 : 7,
		11 : 7,
		12 : 7,
	},
	
	EventType.Story : {
		1  : 22,
		2  : 20,
		3  : 22,
		4  : 22,
		5  : 22,
		6  : 22,
		7  : 22,
		8  : 22,
		9  : 17,
		10 : 22,
		11 : 22,
		12 : 22,
	},
}

StartDateOverride = {
	BannerType.Festival : {
		# "2023-3" : 2,
	},
	
	BannerType.Party : {
		
	},
	
	EventType.Exchange : {
		
	},
	
	EventType.Story : {
		# "2023-3" : 22,
	},
}
