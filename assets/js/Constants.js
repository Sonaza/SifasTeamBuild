
app.value("SiteGlobals",
{
	site_title : "SIFAS Card Rotations",
});

const highlight_options = [
	{ 'value' : '0',          'label' : 'No Highlighting' },
	{ 'value' : '1',          'label' : 'Initial Cards' },
	{ 'value' : '2',          'label' : 'Events & SBL' },
	{ 'value' : '3',          'label' : 'Gacha' },
	{ 'value' : '5',          'label' : 'Spotlight ' },
	{ 'value' : '6',          'label' : 'Festival' },
	{ 'value' : '7',          'label' : 'Party' },
	{ 'value' : 'gacha',      'label' : 'Any Gacha' },
	{ 'value' : 'limited',    'label' : 'Any Limited' },
	{ 'value' : 'muse',       'label' : 'µ\'s Cards' },
	{ 'value' : 'aqours',     'label' : 'Aqours Cards' },
	{ 'value' : 'nijigasaki', 'label' : 'Nijigasaki Cards' },
];

const highlight_map = {
	'none'       : '0',
	'initial'    : '1',
	'event'      : '2',
	'gacha'      : '3',
	'spotlight'  : '5',
	'festival'   : '6',
	'party'      : '7',
	'any_gacha'  : 'gacha',
	'muse'       : 'muse',
	'aqours'     : 'aqours',
	'nijigasaki' : 'nijigasaki',
};

const highlight_reverse_map = {
	'0'          : 'none',
	'1'          : 'initial',
	'2'          : 'event',
	'3'          : 'gacha',
	'5'          : 'spotlight',
	'6'          : 'festival',
	'7'          : 'party',
	'gacha'      : 'any_gacha',
	'limited'    : 'limited',
	'muse'       : 'muse',
	'aqours'     : 'aqours',
	'nijigasaki' : 'nijigasaki',
};

