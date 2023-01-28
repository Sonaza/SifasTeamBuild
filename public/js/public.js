
function storageAvailable(type)
{
	var storage;
	try {
		storage = window[type];
		var x = '__storage_test__';
		storage.setItem(x, x);
		storage.removeItem(x);
		return true;
	}
	catch(e) {
		return e instanceof DOMException && (
			// everything except Firefox
			e.code === 22 ||
			// Firefox
			e.code === 1014 ||
			// test name field too, because code might not be present
			// everything except Firefox
			e.name === 'QuotaExceededError' ||
			// Firefox
			e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
			// acknowledge QuotaExceededError only if there's something already stored
			(storage && storage.length !== 0);
	}
}

let is_in_mobile_mode = () =>
{
	return document.documentElement.clientWidth <= 900
	       || window.matchMedia("(hover: none)").matches
	       || window.matchMedia("(any-hover: none)").matches;
}

let pluralize = function(value, s, p)
{
	return new String(value) + " " + (value == 1 ? s : p);
}

let format_seconds = function(seconds_param)
{
	let days = Math.floor(seconds_param / 86400);
	let hours = Math.floor(seconds_param % 86400 / 3600);
	let minutes = Math.floor(seconds_param % 86400 % 3600 / 60);
	let seconds = Math.floor(seconds_param % 86400 % 3600 % 60);
	
	if (days > 0)
	{
		return pluralize(days, "day", "days") + " ago";
	}
	
	if (hours > 0)
	{
		return pluralize(hours, "hour", "hours") + " ago";
	}
	
	if (minutes > 0)
	{
		return pluralize(minutes, "minute", "minutes") + " ago";
	}
	
	return pluralize(seconds, "second", "seconds") + " ago";
}

const site_title = "SIFAS Card Rotations";

const stats_subpages = {
	'general'     : "General",
	'overdueness' : "Weighted Overdueness",
	'event'       : "Event URs",
	'festival'    : "Festival URs",
	'party'       : "Party URs",
	'limited'     : "Limited URs",
	'spotlight'   : "Party + Spotlight",
	'nonlimited'  : "Non-Limited Gacha UR",
	'gacha'       : "Any Gacha UR",
	'ur'          : "Any UR",
	'sr'          : "Any SR",
	'all'         : "All",
};

const history_subpages = {
	'all'         : "All",
	'event'       : "Event URs",
	'festival'    : "Festival URs",
	'party'       : "Party URs",
	'limited'     : "Limited URs",
	'nonlimited'  : "Non-Limited Gacha UR",
	'gacha'       : "Any Gacha UR",
	'ur'          : "Any UR",
	'sr'          : "Any SR",
};

const history_idols = {
	// µ's idols
	'hanayo'   : 'Hanayo',
	'rin'      : 'Rin',
	'maki'     : 'Maki',
	'honoka'   : 'Honoka',
	'kotori'   : 'Kotori',
	'umi'      : 'Umi',
	'nozomi'   : 'Nozomi',
	'eli'      : 'Eli',
	'nico'     : 'Nico',
	
	// Aqours idols
	'hanamaru' : 'Hanamaru',
	'yoshiko'  : 'Yoshiko',
	'ruby'     : 'Ruby',
	'chika'    : 'Chika',
	'riko'     : 'Riko',
	'you'      : 'You',
	'kanan'    : 'Kanan',
	'dia'      : 'Dia',
	'mari'     : 'Mari',
	
	// Nijigasaki idols
	'rina'     : 'Rina',
	'kasumi'   : 'Kasumi',
	'shizuku'  : 'Shizuku',
	'shioriko' : 'Shioriko',
	'ayumu'    : 'Ayumu',
	'setsuna'  : 'Setsuna',
	'ai'       : 'Ai',
	'lanzhu'   : 'Lanzhu',
	'emma'     : 'Emma',
	'kanata'   : 'Kanata',
	'karin'    : 'Karin',
	'mia'      : 'Mia',
}

const routes = [
	{
		title       : 'UR Rotations',
		path        : '/ur-rotations',
		controller  : 'MainController',
		template    : 'ur_rotations.html',
		exact_match : true,
	},
	{
		title       : 'SR Sets',
		path        : '/sr-sets',
		controller  : 'MainController',
		template    : 'sr_sets.html',
	},
	{
		title       : 'Festival Rotations',
		path        : '/festival',
		controller  : 'MainController',
		template    : 'festival_rotations.html',
	},
	{
		title       : 'Party Rotations',
		path        : '/party',
		controller  : 'MainController',
		template    : 'party_rotations.html',
	},
	{
		title       : 'Event Rotations',
		path        : '/event',
		controller  : 'MainController',
		template    : 'event_rotations.html',
		exact_match : true,
	},
	{
		title       : 'µ\'s Cards',
		path        : '/muse/:page?',
		controller  : 'MainController',
		template    : 'idol_arrays_muse.html',
		hasSubpages : true,
	},
	{
		title       : 'Aqours Cards',
		path        : '/aqours/:page?',
		controller  : 'MainController',
		template    : 'idol_arrays_aqours.html',
		hasSubpages : true,
	},
	{
		title       : 'Nijigasaki Cards',
		path        : '/nijigasaki/:page?',
		controller  : 'MainController',
		template    : 'idol_arrays_nijigasaki.html',
		hasSubpages : true,
	},
	{
		title       : 'Event Cards',
		path        : '/event_cards',
		controller  : 'EventCardsController',
		template    : 'event_cards.html',
		hasSubpages : true,
		exact_match : true,
		// reloadOnSearch : true,
	},
	{
		title       : 'Gacha Banners',
		path        : '/banners',
		controller  : 'BannersController',
		template    : 'banners.html',
		hasSubpages : true,
		exact_match : true,
		// reloadOnSearch : true,
	},
	{
		title       : 'Card Stats',
		path        : '/stats/:page?',
		controller  : 'StatsController',
		template    : function(params)
		{
			if (params.page !== undefined && params.page in stats_subpages)
			{
				if (params.page != 'general')
				{
					return 'stats_' + params.page + '.html';
				}
			}
			else if (params.page === undefined || params.page === 'general')
			{	
				return 'stats.html';
			}
			
			return false;
		},
		templateErrorRedirect    : '/stats',
		hasSubpages : true,
	},
	{
		title       : 'Card History',
		path        : '/history/:idol?/:page?',
		controller  : 'HistoryController',
		template    : function(params)
		{
			if (params.idol !== undefined
				&& params.idol in history_idols)
			{
				if (params.page in history_subpages)
				{
					return 'history/history_' + params.idol + '_' + params.page + '.html';
				}
				else
				{
					return 'history/history_' + params.idol + '_all.html';
				}
			}
			else if (params.idol === undefined)
			{	
				return 'history.html';
			}
			
			return false;
		},
		templateErrorRedirect    : '/history',
		hasSubpages : true,
	},
];

var app = angular.module('app', ['ngRoute', 'ngSanitize', 'ngCookies'],
	function($interpolateProvider)
	{
		$interpolateProvider.startSymbol('[[');
		$interpolateProvider.endSymbol(']]');
	}
)

app.config(function($routeProvider, $locationProvider)
	{
		$routeProvider.when('/', {
			controller:  'MainController',
			templateUrl: 'pages/home.html',
		});

		for (const route of routes)
		{
			$routeProvider.when(route.path, {
				controller:  route.controller,
				templateUrl: function(params)
				{
					if (typeof route.template == "function")
					{
						let page_path = route.template(params);
						if (page_path !== false)
						{
							return 'pages/' + page_path;
						}
						else
						{
							return false;
						}
					}
					
					return 'pages/' + route.template;
				},
				reloadOnSearch: route.reloadOnSearch || false,
				redirectTo : function(route_params, location_path, location_params)
				{
					if (typeof route.template == "function")
					{
						let page_path = route.template(route_params);
						if (page_path === false)
						{
							return route.templateErrorRedirect;
						}
					}
				}
			})
		}

		$routeProvider.otherwise({
			redirectTo: '/',
		});

		$locationProvider.hashPrefix('');
		// $locationProvider.html5Mode(true);
	}
)

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

let getStorage = (key, default_value) =>
{
	if (!storageAvailable('localStorage'))
	{
		return default_value;
	}
	
	let value = window.localStorage.getItem(key);
	if (value === null || value === "null")
	{
		return default_value;
	}
	
	return {
		'boolean'   : (v) => v == 'true',
		'number'    : Number,
		'string'    : String,
		'undefined' : () => console.warn('value type undefined'),
	}[typeof default_value](value);
}

let saveStorage = (values) =>
{
	for (let [key, value] of Object.entries(values))
	{
		window.localStorage.setItem(key, value);
	}
}

let tooltipVisible = false;
let toggleTooltip = function($scope, $event, visible)
{
	// No need to do anything if tooltip is already hidden
	if (visible === false && tooltipVisible === false)
		return;
	
	if ($event !== undefined)
	{
		if (is_in_mobile_mode())
		{
			// Don't accept mouse events, prevents double firing
			if ($event.type == "mouseover" || $event.type == "mouseout")
				return;
			
			if (visible === false)
			{
				// Prevent closing of the tooltip when clicking on the tooltip text.
				// Only close if clicking outside or on the Kirara link
				if (!($event.target.closest('#card-tooltip') !== null &&
					  $event.target.closest('.card-tooltip-inner') === null))
				{
					return;
				}
			}
		}
		else
		{
			// Disable click events on desktop mode
			if ($event.type == 'click')
				return;
		}
	}
	
	let tooltip = document.querySelector("#card-tooltip");
	let tooltip_element = angular.element(tooltip);
	
	tooltipVisible = visible;
	
	// Hide tooltip
	if (visible == false)
	{
		if (!is_in_mobile_mode())
		{
			tooltip.style.visibility = 'hidden';
			tooltip.style.top = '-999px';
			tooltip.style.left = '-999px';
			tooltip.style.right = 'auto';
			tooltip.style.bottom = 'auto';
		}
		
		tooltip_element.removeClass('visible');
		return;
	}
		
	// Happens when auto closing on resize
	if ($event === undefined || $scope === undefined)
	{
		tooltip_element.removeClass('visible');
		tooltip.style.inset = '';
		return;
	}
	
	tooltip_element.addClass('visible');
	
	tooltip.style.visibility = 'visible';
	
	let tooltipDataElement = $event.target.closest('.tooltip-data');
	
	const keys = [
		'member-id', 'member-name',
		'card-status', 'card-ordinal',
		'card-rarity', 'card-attribute', 'card-type',
		'card-title-normal', 'card-title-idolized',
		'card-source', 'card-release-date',
		'card-event', 'stats-tooltip',
	];
	
	$scope.tooltip_data = Object.assign(...keys.flatMap((key) => {
		return {
			[key.replace(/-/g, '_')] : tooltipDataElement.getAttribute('data-' + key)
		}
	}));
	
	if (!$scope.tooltip_data.card_status)
		$scope.tooltip_data.card_status = 1;
	
	if (is_in_mobile_mode())
	{
		// tooltip_element.addClass('mobile-card-tooltip');
		tooltip.style.inset = '';
		return;
	}
	
	let rect = tooltipDataElement.getBoundingClientRect();
	
	const doc = document.documentElement;
	const view_width = doc.clientWidth;
	const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
	
	const flipAnchor = (rect.x > view_width * 0.66) || $scope.tooltip_data.stats_tooltip == 1;
	
	let offset = ($scope.tooltip_data.card_status == 1 ? 
		{x: 15, y: -16} :
		{x: 15, y: -4}
	);
	
	if ($scope.tooltip_data.stats_tooltip)
	{
		offset = {x: 25, y: -26};
	}
	
	if (flipAnchor)
	{
		tooltip.style.top = (rect.top + scroll_top + offset.y) + 'px';
		
		tooltip.style.right = (view_width - rect.left + offset.x) + 'px';
		tooltip.style.left = 'auto';
	}
	else
	{
		tooltip.style.top = (rect.top + scroll_top + offset.y) + 'px';
		
		tooltip.style.left = (rect.right + offset.x) + 'px';
		tooltip.style.right = 'auto';
	}
}

app.run(($rootScope, $window) =>
	{
		$rootScope.settings = {
			use_idolized_thumbnails : getStorage('use_idolized_thumbnails', true),
			order_reversed          : getStorage('order_reversed', false),
			highlight_source        : getStorage('highlight_source', '0'),
			show_tooltips           : getStorage('show_tooltips', true),
			collapsed               : getStorage('collapsed', false),
			hide_empty_rows         : getStorage('hide_empty_rows', false),
			dark_mode               : getStorage('dark_mode', window.matchMedia("(prefers-color-scheme: dark)").matches),
			// alt           : true,
		}
		
		$rootScope.is_in_mobile_mode = is_in_mobile_mode;
		
		$rootScope.disable_scrolling = false;
		$rootScope.scrollDisabler = () =>
		{
			if ($rootScope.disable_scrolling)
			{
				return 'scrolling-disabled';
			}
			return '';
		}
		
		$rootScope.openMobileTooltip = ($event) =>
		{
			if (!is_in_mobile_mode() || !$rootScope.settings.show_tooltips)
			{
				return;
			}
			
			$rootScope.toggleTooltip($event, true);
			$event.preventDefault();
		}
		
		$rootScope.dismissMobileTooltip = ($event) =>
		{
			if (!is_in_mobile_mode())
			{
				return;
			}
			
			$rootScope.toggleTooltip($event, false);
		}
		
		$rootScope.toggleTooltip = ($event, visible) => { toggleTooltip($rootScope, $event, visible); }
		angular.element($window).on('resize', () => { $rootScope.toggleTooltip(undefined, false); });
	}
)

app.controller('BaseController', function($rootScope, $scope, $route, $routeParams, $location, $timeout, $parse, $window, $cookies)
	{
		angular.element(document.querySelector("body")).removeClass('no-js');
		
		const url_options = $location.search();
		if (url_options.idolized !== undefined)
		{
			if (url_options.idolized === 'true' || url_options.idolized == 1)
			{
				$rootScope.settings.use_idolized_thumbnails = true;
			}
			else
			{
				$rootScope.settings.use_idolized_thumbnails = false;
			}
		}
		
		if (url_options.reverse !== undefined)
		{
			if (url_options.reverse === 'true' || url_options.reverse == 1)
			{
				$rootScope.settings.order_reversed = true;
			}
			else
			{
				$rootScope.settings.order_reversed = false;
			}
		}
		
		if (url_options.highlight !== undefined)
		{
			if (url_options.highlight in highlight_map)
			{
				$rootScope.settings.highlight_source = highlight_map[url_options.highlight];
			}
			else
			{
				for (const opt of highlight_options)
				{
					if (opt.value == url_options.highlight)
					{
						$rootScope.settings.highlight_source = opt.value;
						break;
					}
				}
			}
		}
		
		if (!($rootScope.settings.highlight_source in highlight_reverse_map))
		{
			$rootScope.settings.highlight_source = '0';
		}
		
		//////////////////////////////////////////////////
		
		$scope.highlight_options = highlight_options;
		$scope.activeSettingsClass = () =>
		{
			let output = [];
			
			if ($rootScope.settings.use_idolized_thumbnails)
			{
				output.push('use-idolized-thumbnails');
			}
			
			// if ($rootScope.settings.alt)
			// {
			// 	output.push('alt-view');
			// }
			
			if ($rootScope.settings.collapsed)
			{
				output.push('stats-collapsed-tables');
			}
			
			if ($rootScope.settings.hide_empty_rows)
			{
				output.push('stats-hide-empty-rows');
			}
			
			if ($rootScope.settings.order_reversed)
			{
				output.push('order-reversed');
			}
			
			if (!$rootScope.settings.show_tooltips)
			{
				output.push('hide-tooltips');
			}
			
			if ($rootScope.settings.dark_mode)
			{
				output.push('dark-mode');
			}
			
			output.push('source-highlight-' + $rootScope.settings.highlight_source);
			if ($rootScope.settings.highlight_source != '0')
			{
				output.push('source-highlighting-active');
			}
			else
			{
				output.push('source-highlighting-inactive');
			}
			
			if ($scope.navigation_visible || $scope.settings_visible)
			{
				output.push('sidebar-open');
			}
			
			return output.join(' ');
		}
		
		$scope.update_search_params = () =>
		{
			let allowed_keys = ['filter', 'filter_featured', 'filter_highlight', 'banner'];
			let search = $location.search();
			for (let key in search)
			{
				if (allowed_keys.indexOf(key) < 0)
				{
					delete search[key];
				}
			}
			$location.search(search).replace();
			
			if ($rootScope.settings.highlight_source != '0')
			{
				$location.search('highlight', highlight_reverse_map[$rootScope.settings.highlight_source]).replace();
			}
			
			
			// $location.search('idolized', $rootScope.settings.use_idolized_thumbnails ? 'true' : 'false').replace();
			// $location.search('reverse', $rootScope.settings.order_reversed ? 'true' : 'false').replace();
		}
		
		$scope.$watch('$root.settings', function(bs, settings)
		{
			saveStorage($rootScope.settings);
			$timeout(() => {
				$scope.unfocus();
			}, 350);
			
			if (!$rootScope.settings.show_tooltips)
			{
				toggleTooltip(undefined, undefined, false);
			}
			
			let expires = new Date();
			expires.setDate(expires.getDate() + 365);
			if ($rootScope.settings.dark_mode)
			{
				$cookies.put('dark_mode_enabled', 1, {
					expires: expires,
					samesite: 'strict',
				});
			}
			else
			{
				$cookies.put('dark_mode_enabled', 0, {
					expires: expires,
					samesite: 'strict',
				});
			}
			
			$scope.update_search_params();
		}, true);
		
		$scope.$watch('$root.settings.highlight_source', function(bs, settings)
		{
			let e = document.querySelector(".source-selector");
			angular.element(e).addClass('changed');
			$timeout(() => {
				angular.element(e).removeClass('changed');
			}, 200);
		});
		
		$scope.navigation_visible = false;
		$scope.settings_visible = false;
		
		$scope.header_hidden = false;
		$scope.hiddenHeaderActive = () =>
		{
			if ($scope.navigation_visible || $scope.settings_visible)
			{
				return '';
			}
			
			if ($scope.header_hidden)
			{
				return 'header-hidden';
			}
		}
		
		$scope.scroll_accumulator = 0;
		$scope.scroll = (event, diff) =>
		{
			let doc = document.documentElement;
			const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
			if ($scope.header_hidden && scroll_top < 50)
			{
				$scope.scroll_accumulator = 0;
				$scope.header_hidden = false;
				return;
			}
			
			if ((diff < 0 && $scope.scroll_accumulator > 0) || (diff > 0 && $scope.scroll_accumulator < 0))
			{
				$scope.scroll_accumulator = 0;
			}
			
			$scope.scroll_accumulator += diff;
			
			if (diff > 0)
			{
				if ($scope.scroll_accumulator > 150)
				{
					$scope.header_hidden = true;
				}
			}
			else if (diff < 0)
			{
				if ($scope.scroll_accumulator < -200)
				{
					$scope.header_hidden = false;
				}
			}
		}
		
		$scope.toggle = ($event, variable_name) =>
		{
			let variable = $parse(variable_name);
			let value = variable($scope);
			
			$scope.navigation_visible = false;
			$scope.settings_visible = false;
			
			variable.assign($scope, !value);
			
			toggleTooltip(undefined, undefined, false);
		}
		
		$scope.sidebarToggleActive = (value) => 
		{
			if (value)
			{
				return 'visible';
			}
		}
		
		$scope.anySideBarToggleActive = () =>
		{
			if ($scope.navigation_visible || $scope.settings_visible)
			{
				return 'sidebar-visible';
			}
		}
		
		$scope.unfocus = ($event) =>
		{
			$scope.navigation_visible = false;
			$scope.settings_visible = false;
			
			$scope.scroll_accumulator = 0;
			$scope.header_hidden = false;
		}
		
		$scope.tap_unfocus = ($event) =>
		{
			if (!$event) return;
			
			if ($event.target == $event.target.closest('#header'))
			{
				return;
			}
			
			if ($event.target == $event.target.closest('.unfocus-target') || 
				$event.target == $event.target.closest('#side-nav') || 
				$event.target == $event.target.closest('.side-nav-inner') || 
				$event.target == $event.target.closest('.side-nav-ul'))
			{
				$scope.unfocus();
			}
		}
		
		$scope.handle_expiry = function(next_url)
		{
			let now = new Date();
			let now_utc = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), now.getUTCHours(), now.getUTCMinutes(), now.getUTCSeconds()));
			
			if ($scope.page_loaded === undefined)
			{
				$scope.page_loaded = now_utc;
				
				let expiry_dates = [
					new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(),     6, 3, 0)),
					new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + 1, 6, 3, 0)),
				];
				for (const expiry of expiry_dates)
				{
					if (expiry < $scope.page_loaded)
						continue;
					
					$scope.page_expires = expiry;
					break;
				}
				
				console.info("This page was initially loaded on", $scope.page_loaded);
				console.info("This page will expire on", $scope.page_expires);
			}
			
			if (now_utc >= $scope.page_expires)
			{
				location.href = next_url;
				location.reload();
			}
		}
		
		$rootScope.$on("$locationChangeStart", function(event, next, current)
		{ 
			$scope.handle_expiry(next);
			
			$scope.unfocus();
			$scope.update_search_params();
		});
		
		$scope.keydown = ($event) =>
		{
			if ($event.repeat) return;
			
			if (!($event.repeat || $event.ctrlKey || $event.altKey || $event.metaKey))
			{
				if ($event.keyCode == 83) // S-key
				{
					for (let i in highlight_options)
					{
						if (highlight_options[i].value == $rootScope.settings.highlight_source)
						{
							$event.preventDefault();
							
							if (!$event.shiftKey)
							{
								let nextIndex = parseInt(i) + 1; // fuck javascript such a shitty language
							
								if (nextIndex < highlight_options.length)
								{
									$rootScope.settings.highlight_source = highlight_options[nextIndex].value;
								}
								else
								{
									$rootScope.settings.highlight_source = highlight_options[0].value;
								}
							}
							else
							{
								let prevIndex = parseInt(i) - 1; // fuck javascript such a shitty language
								if (prevIndex >= 0)
								{
									$rootScope.settings.highlight_source = highlight_options[prevIndex].value;
								}
								else
								{
									$rootScope.settings.highlight_source = highlight_options[highlight_options.length-1].value;
								}
							}
							return;
						}
					}
				}
				
				if (!$event.shiftKey)
				{
					if ($event.keyCode == 81) // Q-key
					{
						$event.preventDefault();
						$rootScope.settings.use_idolized_thumbnails = !$rootScope.settings.use_idolized_thumbnails;
						return;
					}
					
					if ($event.keyCode == 87) // W-key
					{
						$event.preventDefault();
						$rootScope.settings.order_reversed	 = !$rootScope.settings.order_reversed;
						return;
					}
					
					if ($event.keyCode == 84) // T-key
					{
						$event.preventDefault();
						$rootScope.settings.show_tooltips	 = !$rootScope.settings.show_tooltips;
						return;
					}
					
					if ($event.keyCode == 82) // R-key
					{
						$event.preventDefault();
						$rootScope.settings.use_idolized_thumbnails = true;
						$rootScope.settings.order_reversed          = false;
						$rootScope.settings.highlight_source        = '0';
						// return;
					}
				}
			}
			
			$rootScope.$broadcast('keydown', $event);
			
			angular.element(document.querySelector("#source-selector-default")).remove();
		};
		
		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
)

app.controller('NavController', function($rootScope, $scope, $routeParams, $location)
	{
		$scope.isActive = (viewLocation, exact_match) =>
		{
			if (exact_match)
			{
				return $location.path() === viewLocation;
			}
			else
			{
				return $location.path().startsWith(viewLocation);
			}
		};

		$scope.classActive = (viewLocation, exact_match) =>
		{
			if ($scope.isActive(viewLocation, exact_match))
			{
				return 'active';
			}
		}
		
		$rootScope.$on('$locationChangeSuccess', (event) =>
		{
			if ($scope.filter_options === undefined)
			{
				$scope.filter_options = "";
			}
			
			let url =  $location.url().split('?');
			if (url.length >= 2)
			{
				$scope.filter_options = "?" + url[1];
			}
		});
		
		$scope.$on('keydown', (_, e) =>
		{
			if (e.repeat || e.ctrlKey || e.altKey || e.metaKey) return;
			
			if (!e.shiftKey)
			{
				if (e.keyCode == 82) // R-key
				{
					e.preventDefault();
					$scope.filter_options = "";
					return;
				}
			}
		});
		
		$scope.$on('update-title', (_, sub_title) =>
		{
			if ($location.path() == '/')
			{
				$rootScope.title = site_title;
			}
			else
			{
				for (const route of routes)
				{
					let basepath = '/' + route['path'].split('/')[1];
					
					if ($scope.isActive(basepath, route['exact_match']))
					{
						if (route.hasSubpages && sub_title !== undefined)
						{
							$rootScope.title = route['title'] + " / " + sub_title + " &mdash; " + site_title;
						}
						else
						{
							$rootScope.title = route['title'] + " &mdash; " + site_title;
						}
						break;
					}
				}
			}
		})
	}
)


app.directive('ellipsisBullshit', function($window)
{
	return {
		restrict: 'A',
		link: function (scope, elements, attrs)
		{
			let element = elements[0];
			if (!element) return;
			
			let parent_selector = attrs['ellipsisBullshit'];
			if (!parent_selector) return;
			
			let parent = element.closest(parent_selector);
			if (!parent) return;
			
			let update = (event) =>
			{
				if (element.offsetWidth < element.scrollWidth)
				{
					angular.element(parent).addClass('text-overflowed');
				}
				else
				{
					angular.element(parent).removeClass('text-overflowed');
				}
			}
			update();
			
			angular.element($window).on('resize scroll', update);
		}
	}
})

const MEMBERS_ORDERED = [
	{ id: -1,  name: "— Show All —",      group: undefined,    grouptag: undefined },
	{ id: 8,   name: "Hanayo Koizumi",    group: "µ's",        grouptag: "muse" },
	{ id: 5,   name: "Rin Hoshizora",     group: "µ's",        grouptag: "muse" },
	{ id: 6,   name: "Maki Nishikino",    group: "µ's",        grouptag: "muse" },
	{ id: 1,   name: "Honoka Kousaka",    group: "µ's",        grouptag: "muse" },
	{ id: 3,   name: "Kotori Minami",     group: "µ's",        grouptag: "muse" },
	{ id: 4,   name: "Umi Sonoda",        group: "µ's",        grouptag: "muse" },
	{ id: 7,   name: "Nozomi Toujou",     group: "µ's",        grouptag: "muse" },
	{ id: 2,   name: "Eli Ayase",         group: "µ's",        grouptag: "muse" },
	{ id: 9,   name: "Nico Yazawa",       group: "µ's",        grouptag: "muse" },
	{ id: 107, name: "Hanamaru Kunikida", group: "Aqours",     grouptag: "aqours" },
	{ id: 106, name: "Yoshiko Tsushima",  group: "Aqours",     grouptag: "aqours" },
	{ id: 109, name: "Ruby Kurosawa",     group: "Aqours",     grouptag: "aqours" },
	{ id: 101, name: "Chika Takami",      group: "Aqours",     grouptag: "aqours" },
	{ id: 102, name: "Riko Sakurauchi",   group: "Aqours",     grouptag: "aqours" },
	{ id: 105, name: "You Watanabe",      group: "Aqours",     grouptag: "aqours" },
	{ id: 103, name: "Kanan Matsuura",    group: "Aqours",     grouptag: "aqours" },
	{ id: 104, name: "Dia Kurosawa",      group: "Aqours",     grouptag: "aqours" },
	{ id: 108, name: "Mari Ohara",        group: "Aqours",     grouptag: "aqours" },
	{ id: 209, name: "Rina Tennouji",     group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 202, name: "Kasumi Nakasu",     group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 203, name: "Shizuku Ousaka",    group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 210, name: "Shioriko Mifune",   group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 201, name: "Ayumu Uehara",      group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 207, name: "Setsuna Yuuki",     group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 205, name: "Ai Miyashita",      group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 212, name: "Lanzhu Zhong",      group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 208, name: "Emma Verde",        group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 206, name: "Kanata Konoe",      group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 204, name: "Karin Asaka",       group: "Nijigasaki", grouptag: "nijigasaki" },
	{ id: 211, name: "Mia Taylor",        group: "Nijigasaki", grouptag: "nijigasaki" },
];

app.controller('EventCardsController', function($rootScope, $scope, $route, $routeParams, $location, $window)
	{
		$scope.loading = true;
		
		if ($routeParams.page === undefined)
		{
			window.scrollTo(0, 0);
		}
		
		$scope.filter_index = 0;
		$scope.filter_index_max = MEMBERS_ORDERED.length - 1;
		
		$scope.filter_settings = {
			filter        : -1,
			highlight     : false,
			featured_only : false,
		};
		
		$scope.filter_idol = MEMBERS_ORDERED[0];
		$scope.select_box_options_opened = false;
		
		$scope.last_toggled = 0;
		$scope.toggleSelectBox = ($event) =>
		{
			let t = new Date().getTime();
			if ((t - $scope.last_toggled) < 50) return;
			$scope.last_toggled = t;
			
			$scope.select_box_options_opened = !$scope.select_box_options_opened;
			if ($scope.select_box_options_opened)
			{
				// Lol wtf
				setTimeout($scope.keepSelectBoxOnScreen, 50);
				setTimeout($scope.keepSelectBoxOnScreen, 100);
				setTimeout($scope.keepSelectBoxOnScreen, 150);
			}
			
			$rootScope.disable_scrolling = $scope.select_box_options_opened;
		}
		
		$scope.optionSelectedClass = (member_id) =>
		{
			if (member_id === -1 && $scope.filter_index == 0)
			{
				return 'selected';
			}
			
			if (MEMBERS_ORDERED[$scope.filter_index].id === member_id)
			{
				return 'selected';
			}
			return '';
		}
		
		$scope.selectBoxOptionsClass = () =>
		{
			if ($scope.select_box_options_opened)
			{
				return 'opened'
			}
			else
			{
				return 'hidden';
			}
		}
		
		$scope.chooseSelectOption = ($event, member_id) =>
		{
			if (member_id === -1)
			{
				$scope.filter_settings.filter = -1;
			}
			else
			{
				for (let i = 0; i < MEMBERS_ORDERED.length; i++)
				{
					if (MEMBERS_ORDERED[i].id == -1)
						continue;
					
					if (MEMBERS_ORDERED[i].id === member_id)
					{
						$scope.filter_settings.filter = MEMBERS_ORDERED[i].id;
						break;
					}
				}
			}
			
			$scope.toggleSelectBox($event);
		}
		
		$scope.keepSelectBoxOnScreen = (event) =>
		{
			let e = document.querySelector('.select-box-options');
			if (!e) return;
			
			const view_width = document.documentElement.clientWidth;
			if (view_width < 900)
			{
				angular.element(e).css('margin-left', '0');
				return;
			}
			let rect = e.getBoundingClientRect();
			
			var style = e.currentStyle || window.getComputedStyle(e);
			let current_margin = parseFloat(style.marginLeft);
			
			let margin = Math.min((view_width - rect.right) - 20 + current_margin, 0);
			angular.element(e).css('margin-left', margin + "px");
		}
		angular.element($window).on('resize scroll', $scope.keepSelectBoxOnScreen);
		$scope.keepSelectBoxOnScreen();
		
		const url_options = $location.search();
		if (url_options.filter !== undefined)
		{
			let filter_string = url_options.filter.toLowerCase().trim();
			if (filter_string !== 'none')
			{
				for (let i = 0; i < MEMBERS_ORDERED.length; i++)
				{
					if (MEMBERS_ORDERED[i].id == -1)
						continue;
					
					let first_name = MEMBERS_ORDERED[i].name.split(' ')[0].toLowerCase();
					if (first_name === filter_string)
					{
						$scope.filter_settings.filter = MEMBERS_ORDERED[i].id;
						break;
					}
				}
			}
		}
		if (url_options.filter_featured !== undefined)
		{
			if (url_options.filter_featured == 'true' || url_options.filter_featured == '1')
			{
				$scope.filter_settings.featured_only = true;
			}
		}
		if (url_options.filter_highlight !== undefined)
		{
			if (url_options.filter_highlight == 'true' ||  url_options.filter_highlight == '1')
			{
				$scope.filter_settings.highlight = true;
			}
		}
		
		$scope.filterEventsClass = (s) =>
		{
			let output = [];
			
			if ($scope.filter_settings.highlight !== false)
			{
				output.push('highlight');
			}
			
			if ($scope.filter_settings.filter != -1)
			{
				output.push('filtering-active');
				output.push('show-idol-' + $scope.filter_settings.filter);
				
				if ($scope.filter_settings.featured_only)
				{
					output.push('featured-only');
				}
			}
			
			return output.join(' ');
		}
		
		$scope.$watch('filter_settings', function(a, b)
		{
			if ($scope.filter_settings.featured_only)
			{
				$location.search('filter_featured', 'true').replace();
			}
			else
			{
				$location.search('filter_featured', undefined).replace();
			}
			
			if ($scope.filter_settings.highlight)
			{
				$location.search('filter_highlight', 'true').replace();
			}
			else
			{
				$location.search('filter_highlight', undefined).replace();
			}
		}, true)
		
		$scope.$watch('filter_settings.filter', function(a, b)
		{
			for (let i = 0; i < MEMBERS_ORDERED.length; i++)
			{
				if (MEMBERS_ORDERED[i].id == $scope.filter_settings.filter)
				{
					$scope.filter_index = i;
					$scope.filter_idol = MEMBERS_ORDERED[i];
					
					if (MEMBERS_ORDERED[i].id != -1)
					{
						let first_name = MEMBERS_ORDERED[i].name.split(' ')[0].toLowerCase();
						$location.search('filter', first_name).replace();
						
						// $rootScope.$broadcast('update-title', MEMBERS_ORDERED[i].name.split(' ')[0]);
					}
					else
					{
						$location.search('filter', undefined).replace();
						// $rootScope.$broadcast('update-title');
					}
					
					break;
				}
			}
		});
		
		$rootScope.$broadcast('update-title');
		
		$scope.$on('keydown', (_, e) =>
		{
			if (e.repeat || e.ctrlKey || e.altKey || e.metaKey) return;
			
			// document.querySelector('#filter-event-cards').blur();
			
			if (e.keyCode == 69) // E-key
			{
				$scope.filter_index += (e.shiftKey ? -1 : 1);
				if ($scope.filter_index < 0)
				{
					$scope.filter_index = $scope.filter_index_max;
				}
				else if ($scope.filter_index > $scope.filter_index_max)
				{
					$scope.filter_index = 0;
				}
				
				$scope.filter_settings.filter = MEMBERS_ORDERED[$scope.filter_index].id;
				return;
			}
			
			if (!e.shiftKey)
			{
				if (e.keyCode == 70) // F-key
				{
					e.preventDefault();
					$scope.filter_settings.featured_only = !$scope.filter_settings.featured_only;
					return;
				}
				
				if (e.keyCode == 72) // H-key
				{
					e.preventDefault();
					$scope.filter_settings.highlight = !$scope.filter_settings.highlight;
					return;
				}
				
				if (e.keyCode == 82) // R-key
				{
					$scope.filter_settings.filter        = -1;
					$scope.filter_settings.highlight     = false;
					$scope.filter_settings.featured_only = false;
					return;
				}
			}
		});
		
		$scope.loading = false;
	}
);

app.controller('BannersController', function($rootScope, $scope, $route, $routeParams, $location, $window)
	{
		$scope.loading = true;
		
		if ($routeParams.page === undefined)
		{
			window.scrollTo(0, 0);
		}
		
		$scope.filter_index = 0;
		$scope.filter_index_max = MEMBERS_ORDERED.length - 1;
		
		$scope.banner_types = [
			{ id: -1, title: '— Show All —' },
			{ id: 1,  title: 'Spotlight' },
			{ id: 2,  title: 'Festival'  },
			{ id: 3,  title: 'Party'     },
			// { id: 4,  title: 'Other'     },
		];
		
		$scope.banner_index = 0;
		$scope.banner_index_max = $scope.banner_types.length - 1;
		
		$scope.filter_settings = {
			filter        : -1,
			banner        : -1,
			highlight     : false,
		};
		
		$scope.filter_idol = MEMBERS_ORDERED[0];
		$scope.select_box_options_opened = false;
		
		$scope.last_toggled = 0;
		$scope.toggleSelectBox = ($event) =>
		{
			let t = new Date().getTime();
			if ((t - $scope.last_toggled) < 50) return;
			$scope.last_toggled = t;
		
			$scope.select_box_options_opened = !$scope.select_box_options_opened;
			if ($scope.select_box_options_opened)
			{
				// Lol wtf
				setTimeout($scope.keepSelectBoxOnScreen, 50);
				setTimeout($scope.keepSelectBoxOnScreen, 100);
				setTimeout($scope.keepSelectBoxOnScreen, 150);
			}
			
			$rootScope.disable_scrolling = $scope.select_box_options_opened;
		}
		
		$scope.optionSelectedClass = (member_id) =>
		{
			if (member_id === -1 && $scope.filter_index == 0)
			{
				return 'selected';
			}
			
			if (MEMBERS_ORDERED[$scope.filter_index].id === member_id)
			{
				return 'selected';
			}
			return '';
		}
		
		$scope.selectBoxOptionsClass = () =>
		{
			if ($scope.select_box_options_opened)
			{
				return 'opened'
			}
			else
			{
				return 'hidden';
			}
		}
		
		$scope.chooseSelectOption = ($event, member_id) =>
		{
			if (member_id === -1)
			{
				$scope.filter_settings.filter = -1;
			}
			else
			{
				for (let i = 0; i < MEMBERS_ORDERED.length; i++)
				{
					if (MEMBERS_ORDERED[i].id == -1)
						continue;
					
					if (MEMBERS_ORDERED[i].id === member_id)
					{
						$scope.filter_settings.filter = MEMBERS_ORDERED[i].id;
						break;
					}
				}
			}
			
			$scope.toggleSelectBox($event);
		}
		
		$scope.keepSelectBoxOnScreen = (event) =>
		{
			let e = document.querySelector('.select-box-options');
			if (!e) return;
			
			const view_width = document.documentElement.clientWidth;
			if (view_width < 900)
			{
				angular.element(e).css('margin-left', '0');
				return;
			}
			
			let rect = e.getBoundingClientRect();
			
			var style = e.currentStyle || window.getComputedStyle(e);
			let current_margin = parseFloat(style.marginLeft);
			
			let margin = Math.min((view_width - rect.right) - 20 + current_margin, 0);
			angular.element(e).css('margin-left', margin + "px");
		}
		angular.element($window).on('resize scroll', $scope.keepSelectBoxOnScreen);
		$scope.keepSelectBoxOnScreen();
		
		const url_options = $location.search();
		if (url_options.filter !== undefined)
		{
			let filter_string = url_options.filter.toLowerCase().trim();
			if (filter_string !== 'none')
			{
				for (let i = 0; i < MEMBERS_ORDERED.length; i++)
				{
					if (MEMBERS_ORDERED[i].id == -1)
						continue;
					
					let first_name = MEMBERS_ORDERED[i].name.split(' ')[0].toLowerCase();
					if (first_name === filter_string)
					{
						$scope.filter_settings.filter = MEMBERS_ORDERED[i].id;
						break;
					}
				}
			}
		}
		if (url_options.banner !== undefined)
		{
			let filter_string = url_options.banner.toLowerCase().trim();
			if (filter_string !== 'none')
			{
				for (let i = 0; i < $scope.banner_types.length; i++)
				{
					if ($scope.banner_types[i].id == -1)
						continue;
					
					let type_title = $scope.banner_types[i].title.toLowerCase();
					if (type_title === filter_string)
					{
						$scope.filter_settings.banner = $scope.banner_types[i].id;
						break;
					}
				}
			}
		}
		
		if (url_options.filter_highlight !== undefined)
		{
			if (url_options.filter_highlight == 'true' ||  url_options.filter_highlight == '1')
			{
				$scope.filter_settings.highlight = true;
			}
		}
		
		$scope.filterBannersClass = (s) =>
		{
			let output = [];
			
			if ($scope.filter_settings.highlight !== false)
			{
				output.push('highlight');
			}
			
			if ($scope.filter_settings.filter != -1)
			{
				output.push('filtering-active');
				// output.push('filtering-by-idol');
				output.push('show-idol-' + $scope.filter_settings.filter);
			}
			
			if ($scope.filter_settings.banner != -1)
			{
				output.push('filtering-banner-types');
				for (const banner_type of $scope.banner_types)
				{
					if (banner_type.id != $scope.filter_settings.banner)
					{
						output.push('hide-banner-' + banner_type.id);
					}
				}
				output.push('hide-banner-4');
			}
			
			return output.join(' ');
		}
		
		$scope.$watch('filter_settings', function(a, b)
		{
			if ($scope.filter_settings.highlight)
			{
				$location.search('filter_highlight', 'true').replace();
			}
			else
			{
				$location.search('filter_highlight', undefined).replace();
			}
			$rootScope.$broadcast('refresh-deferred-loads');
		}, true)
		
		$scope.$watch('filter_settings.filter', function(a, b)
		{
			for (let i = 0; i < MEMBERS_ORDERED.length; i++)
			{
				if (MEMBERS_ORDERED[i].id == $scope.filter_settings.filter)
				{
					$scope.filter_index = i;
					$scope.filter_idol = MEMBERS_ORDERED[i];
					
					if (MEMBERS_ORDERED[i].id != -1)
					{
						let first_name = MEMBERS_ORDERED[i].name.split(' ')[0].toLowerCase();
						$location.search('filter', first_name).replace();
					}
					else
					{
						$location.search('filter', undefined).replace();
					}
					
					break;
				}
			}
			$rootScope.$broadcast('refresh-deferred-loads');
		});
		
		$scope.$watch('filter_settings.banner', function(a, b)
		{
			for (let i = 0; i < $scope.banner_types.length; i++)
			{
				if ($scope.banner_types[i].id == $scope.filter_settings.banner)
				{
					$scope.banner_index = i;
					
					if ($scope.banner_types[i].id != -1)
					{
						let type_title = $scope.banner_types[i].title.toLowerCase();
						$location.search('banner', type_title).replace();
					}
					else
					{
						$location.search('banner', undefined).replace();
					}
					
					break;
				}
			}
			$rootScope.$broadcast('refresh-deferred-loads');
		});
		
		$rootScope.$broadcast('update-title');
		
		$scope.$on('keydown', (_, e) =>
		{
			if (e.repeat || e.ctrlKey || e.altKey || e.metaKey) return;
			
			// document.querySelector('#filter-event-cards').blur();
			
			if (e.keyCode == 69) // E-key
			{
				$scope.filter_index += (e.shiftKey ? -1 : 1);
				if ($scope.filter_index < 0)
				{
					$scope.filter_index = $scope.filter_index_max;
				}
				else if ($scope.filter_index > $scope.filter_index_max)
				{
					$scope.filter_index = 0;
				}
				
				$scope.filter_settings.filter = MEMBERS_ORDERED[$scope.filter_index].id;
				return;
			}
			
			if (e.keyCode == 66) // B-key
			{
				$scope.banner_index += (e.shiftKey ? -1 : 1);
				
				if ($scope.banner_index < 0)
				{
					$scope.banner_index = $scope.banner_index_max;
				}
				else if ($scope.banner_index > $scope.banner_index_max)
				{
					$scope.banner_index = 0;
				}
				
				$scope.filter_settings.banner = $scope.banner_types[$scope.banner_index].id;
				return;
			}
			
			if (!e.shiftKey)
			{
				if (e.keyCode == 72) // H-key
				{
					e.preventDefault();
					$scope.filter_settings.highlight = !$scope.filter_settings.highlight;
					return;
				}
				
				if (e.keyCode == 82) // R-key
				{
					$scope.filter_settings.filter     = -1;
					$scope.filter_settings.banner     = -1;
					$scope.filter_settings.highlight  = false;
					return;
				}
			}
		});
		
		$scope.loading = false;
	}
);

app.controller('MainController', function($rootScope, $scope, $route, $routeParams, $location, $window)
	{
		$scope.loading = true;
		
		if ($routeParams.page === undefined)
		{
			window.scrollTo(0, 0);
		}

		$scope.active_page = $routeParams.page;
		if ($scope.active_page === undefined)
		{
			$scope.active_page = 0;
		}

		$scope.isActive = (page) =>
		{
			return $scope.active_page == page;
		}

		$scope.pageActive = (page) =>
		{
			if ($scope.isActive(page))
			{
				return 'active';
			}
		}
		
		angular.element(document.querySelector('.rotation-column-wrapper')).on('scroll', ($event) =>
		{
			$rootScope.$broadcast('refresh-deferred-loads');
		});
		
		let num_pages = undefined;
		let page_selector = document.querySelector('.array-group-page-selector');
		if (page_selector)
		{
			num_pages = parseInt(page_selector.getAttribute('data-num-pages'));
		}
		
		$scope.$on('keydown', (_, e) =>
		{
			if (e.repeat || e.ctrlKey || e.altKey || e.metaKey || e.shiftKey) return;
			
			if (num_pages !== undefined)
			{
				let number = parseInt(e.key);
				if (number !== undefined)
				{
					if (number == 0) number = 10;
					let index = number - 1;
					if (index < num_pages)
					{
						e.preventDefault();
						$route.updateParams({'page': number - 1});
					}
					return;
				}
			}
		});
		
		let page_subtitle = "Page " + (parseInt($scope.active_page) + 1);
		$rootScope.$broadcast('update-title', page_subtitle);

		$scope.loading = false;

		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
)

app.controller('FooterController', function($rootScope, $scope)
	{
		$scope.time_since = (iso_timestamp) =>
		{
			let time = new Date(iso_timestamp);
			if (!time) return "";
			let secondsDiff = (new Date().getTime() - time.getTime()) / 1000;
			return " (" + format_seconds(secondsDiff) + ")";
		}
	}
)

app.controller('StatsController', function($rootScope, $scope, $route, $routeParams, $location, $timeout, $window)
	{
		$scope.loading = true;
		
		if ($routeParams.page === undefined)
		{
			window.scrollTo(0, 0);
		}
		
		$scope.active_page = $routeParams.page;
		if ($scope.active_page === undefined)
		{
			$scope.active_page = 'general';
		}

		$scope.isActive = (page) =>
		{
			return $scope.active_page == page;
		}

		$scope.pageActive = (page) =>
		{
			if ($scope.isActive(page))
			{
				return 'active';
			}
		}

		$scope.get_subtitle = (page) =>
		{
			if (stats_subpages[page])
			{
				return stats_subpages[page];
			}
			return "";
		}
		
		$scope.$on('keydown', (_, e) =>
		{
			if (e.repeat || e.shiftKey || e.ctrlKey || e.altKey || e.metaKey) return;
			
			let number = parseInt(e.key);
			if (number !== undefined)
			{
				if (number == 0) number = 10;
				let index = number - 1;
				
				let keys = Object.keys(stats_subpages);
				if (index < keys.length)
				{
					e.preventDefault();
					$route.updateParams({'page': keys[index]});
					// $scope.$apply();
					return;
				}
			}
			
			if (e.keyCode == 67) // C-key
			{
				e.preventDefault();
				$rootScope.settings.collapsed	     = !$rootScope.settings.collapsed;
			}
			
			if (e.keyCode == 72) // H-key
			{
				e.preventDefault();
				$rootScope.settings.hide_empty_rows  = !$rootScope.settings.hide_empty_rows;
			}
		});
		
		setTimeout(() => {
			const scroller = document.querySelector('.stats-page-selector');
			const active = document.querySelector('.stats-page-selector a.active');
			if (!scroller || !active) return;
			
			const scroller_rect = scroller.getBoundingClientRect();
			const scroller_width = scroller_rect.right - scroller_rect.left;
			
			const element = active.closest('li');
			
			const active_rect = element.getBoundingClientRect();
			const active_width = active_rect.right - active_rect.left;
			
			scroller.scrollLeft = active_rect.left - (scroller_width - active_width) / 2 - scroller_rect.left;
		});

		let page_subtitle = $scope.get_subtitle($scope.active_page);
		$rootScope.$broadcast('update-title', page_subtitle);

		$scope.loading = false;

		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
)

app.controller('HistoryController', function($rootScope, $scope, $route, $routeParams, $location, $timeout, $window)
	{
		$scope.loading = true;
		
		if ($routeParams.page === undefined)
		{
			window.scrollTo(0, 0);
		}
		
		$scope.getIdolGroup = (idol) =>
		{
			for (const member of MEMBERS_ORDERED)
			{
				if (member.id <= 0)
					continue;
				
				let first_name = member.name.split(' ')[0].toLowerCase();
				if (first_name == idol)
				{
					return member.grouptag;
				}
			}
			return false;
		}
			
		$scope.idol_navigation = {
			'group'	     : $scope.getIdolGroup($routeParams.idol),
			'idol'       : $routeParams.idol,
			'idol_group' : $scope.getIdolGroup($routeParams.idol),
		};
		
		$scope.setGroup = (group) => 
		{
			$scope.idol_navigation.group = group;
			
			if (group == $scope.idol_navigation.idol_group)
			{
				setTimeout($scope.scrollPageSelectors);
			}
		}
		
		$scope.active_page = $routeParams.page;
		if ($scope.active_page === undefined)
		{
			$scope.active_page = 'all';
		}

		$scope.isActive = (page) =>
		{
			return $scope.active_page == page;
		}

		$scope.groupActive = (group) =>
		{
			if ($scope.idol_navigation.group == group)
			{
				return 'active';
			}
		}

		$scope.idolActive = (idol) =>
		{
			if ($scope.idol_navigation.idol == idol)
			{
				return 'active border-color-highlight bg-color-highlight';
			}
		}

		$scope.pageActive = (page) =>
		{
			if ($scope.isActive(page))
			{
				return 'active';
			}
		}

		$scope.get_subtitle = (idol, page) =>
		{
			if (idol)
			{
				let idol_name = history_idols[idol];
				if (history_subpages[page])
				{
					// return idol_name + " - " + history_subpages[page];
					return idol_name;
				}
			}
			
			return undefined;
		}
		
		$scope.$on('keydown', (_, e) =>
		{
			if (e.repeat || e.shiftKey || e.ctrlKey || e.altKey || e.metaKey) return;
			
			let number = parseInt(e.key);
			if (number !== undefined)
			{
				if (number == 0) number = 10;
				let index = number - 1;
				
				let keys = Object.keys(history_subpages);
				if (index < keys.length)
				{
					e.preventDefault();
					$route.updateParams({'page': keys[index]});
					// $scope.$apply();
					return;
				}
			}
		});
		
		$scope.scrollPageSelectors = () =>
		{
			const scrollers = document.querySelectorAll('.page-selector');
			for (let scroller of scrollers)
			{
				const active = scroller.querySelector('a.active');
				if (!scroller || !active) continue;
				
				scroller.scrollLeft = 0;
				
				const scroller_rect = scroller.getBoundingClientRect();
				const scroller_width = scroller_rect.right - scroller_rect.left;
				
				const element = active.closest('li');
				
				const active_rect = element.getBoundingClientRect();
				const active_width = active_rect.right - active_rect.left;
				
				scroller.scrollLeft = active_rect.left - (scroller_width - active_width) / 2 - scroller_rect.left;
			}
		}
		
		setTimeout($scope.scrollPageSelectors);

		let page_subtitle = $scope.get_subtitle($routeParams.idol, $scope.active_page);
		$rootScope.$broadcast('update-title', page_subtitle);

		$scope.loading = false;

		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
)

app.directive('pillButton', function($parse, $timeout)
{
	return {
		restrict: 'A',
		transclude: true,
		scope: {
			// variable: '=model',
			// keybind: '=keybind',
		},
		template: '<div class="inner"><div class="inner-dot">&nbsp;</div></div><div class="label">[[ label ]] <span class="hide-mobile" ng-if="keybind">([[ keybind ]])</span></div>',
		controller: function($scope, $transclude)
		{
			$transclude(function(clone, scope)
			{
				$scope.label = angular.element('<div>').append(clone).html();
			});
		},
		link: function (scope, element, attrs)
		{
			let e = angular.element(element[0]); //.querySelector('div.pill-button');
			
			e.addClass('pill-button');
			
			scope.keybind = attrs.keybind;
			
			element.on('mousedown', function(event)
			{
				event.preventDefault();
				$parse(attrs.model).assign(scope.$parent, !$parse(attrs.model)(scope.$parent));
				scope.$parent.$apply();
			});

			scope.$parent.$watch(attrs.model, function(value)
			{
				if (value)
				{
					e.addClass('active').addClass('changed');
				}
				else
				{
					e.removeClass('active');
				}
				
				e.addClass('changed');
				$timeout(() => {
					e.removeClass('changed');
				}, 200);
			});
		}
	}
})

app.directive('cardTooltip', function($parse)
{
	return {
		restrict: 'A',
		// templateUrl: 'tooltip.html?ad',
		template: '<div class="card-tooltip-inner" ng-class="\'idol-\' + data.member_id"><div class="member-info idol-bg-color-dark idol-bg-glow-border"><div class="name">[[ data.member_name ]]</div><div class="card-info" ng-if="data.card_status == 1"><span class="icon-32" ng-class="\'rarity-\' + data.card_rarity"></span><span class="icon-32" ng-class="\'attribute-\' + data.card_attribute"></span><span class="icon-32" ng-class="\'type-\' + data.card_type"></span></div></div><table class="card-details" ng-if="data.card_status == 1"><colgroup><col class="card-detail-label"><col class="card-detail-data"></colgroup><tr class="card-title"><td colspan="2">&#12300;<span class="normal">[[ data.card_title_normal ]]</span><span class="idolized">[[ data.card_title_idolized ]]</span>&#12301;</td></tr><tr class="spacer-top"><th>Source</th><td>[[ data.card_source ]]</td></tr><tr ng-if="data.card_event"><th>Related Event</th><td>[[ data.card_event ]]</td></tr><tr><th>Release Date</th><td>[[ data.card_release_date ]]</td></tr><tr class="card-kirara-link" ng-if="is_in_mobile_mode() && data.card_ordinal != undefined"><td colspan="2"><a href="https://allstars.kirara.ca/card/[[ data.card_ordinal ]]" target="_blank"><i class="fa fa-globe"></i> View on Kirara Database &raquo;</a></td></tr></table><div class="card-details card-missing" ng-if="data.card_status == 2"><b>[[ first_name ]]</b> has yet to receive a card in this cycle.</div><div class="card-details card-missing" ng-if="data.card_status == 3"><b>[[ first_name ]]</b> did not receive a card in this cycle.</div></div>',
		link: function (scope, element, attrs)
		{
			scope.$watch(attrs.cardTooltip, function(value)
			{
				if (value)
				{
					scope.data = value;
					scope.first_name = value.member_name.split(' ')[0];
				}
			}, true);
		}
	}
})

app.directive('deferredLoad', function($parse, $window)
{
	return {
		restrict: 'A',
		scope: true,
		template: '<ng-include class="deferred-load" src="getTemplateUrl()">',
		link: function (scope, element, attrs)
		{
			function isElementInViewport(el)
			{
			    var rect = el.getBoundingClientRect();
			    return (
			        rect.top >= 0 &&
			        rect.left >= 0 &&
			        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /* or $(window).height() */
			        rect.right <= (window.innerWidth || document.documentElement.clientWidth) /* or $(window).width() */
			    );
			}
			function isElementPartiallyInViewport(el)
			{
			    var rect = el.getBoundingClientRect();
			    let width = rect.right - rect.left;
			    let height = rect.bottom - rect.top;
			    return (
			        rect.top >= -height &&
			        rect.left >= -width &&
			        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + height &&
			        rect.right <= (window.innerWidth || document.documentElement.clientWidth) + width
			    );
			}
			
			scope.$on('refresh-deferred-loads', (_) => {
				scope.$apply();
			});
			
			scope.template_url = 'pages/deferred/' + attrs.deferredLoad + '.html';
			
			scope.getTemplateUrl = function()
			{
				// console.log("scope.getTemplateUrl called", attrs.deferredLoad, scope.template_url);
				
				if (!is_in_mobile_mode() && scope.loaded)
				{
					return scope.template_url;
				}
				
				if (isElementPartiallyInViewport(element[0]))
				{
					// console.log("Loading", attrs.deferredLoad);
					scope.loaded = true;
					return scope.template_url;
				}
				
				// console.log("Unloading", attrs.deferredLoad);
				scope.loaded = false;
				return '';
			}
		}
	}
})

app.directive('scroll', function($parse, $window)
{
	return {
		link: function (scope, element, attrs)
		{
			let get_current_scroll = () =>
			{
				let doc = document.documentElement;
				return (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
			}
			let lastScroll = get_current_scroll();
			angular.element($window).on('scroll', function (e)
			{
				const current = get_current_scroll();
				const diff = current - lastScroll;
				lastScroll = current;
				scope.$apply(function()
				{
					scope.$eval(attrs.scroll, {$event: e, diff: diff});
				});
			});
		}
	}
});
