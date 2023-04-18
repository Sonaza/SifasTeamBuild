from IdolDatabase.Enums import *

member_delays_by_rarity = {
	Rarity.SR : {
		Member.Shioriko : [0, 3, 2, ],
		Member.Lanzhu   : [0, 8, ],
		Member.Mia      : [0, 8, ],
	},
	Rarity.UR : {
		Member.Shioriko : [3, 0, 0, 1],
		Member.Lanzhu   : 7,
		Member.Mia      : 7,
	},
}

member_delays_by_source = {
	Source.Event : {
		Member.Shioriko : 1,
		Member.Lanzhu   : 1,
		Member.Mia      : 1,
	},
	Source.Festival : {
		Member.Shioriko : 0,
		Member.Lanzhu   : 2,
		Member.Mia      : 2,
	},
	Source.Party : {
		Member.Shioriko : 0,
		Member.Lanzhu   : 0,
		Member.Mia      : 0,
	},
}

set_title_overrides = {
	Rarity.SR : {
		Group.Nijigasaki : dict([
			(0,  "1st Nijigasaki Solo"),
			(5,  "3rd Nijigasaki Solo"),
		])
	}
}
