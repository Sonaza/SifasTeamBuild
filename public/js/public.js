
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
	'general'    : "General",
	'event'      : "Event URs",
	'festival'   : "Festival URs",
	'party'      : "Party URs",
	'limited'    : "Limited URs",
	'spotlight'  : "Party + Spotlight",
	'nonlimited' : "Non-Limited Gacha UR",
	'gacha'      : "Any Gacha UR",
	'ur'         : "Any UR",
	'sr'         : "Any SR",
};

const routes = [
	{
		title       : 'UR Rotations',
		path        : '/ur-rotations',
		controller  : 'MainController',
		template    : 'ur_rotations.html',
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
		title       : 'SR Sets',
		path        : '/sr-sets',
		controller  : 'MainController',
		template    : 'sr_sets.html',
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
];

var app = angular.module('app', ['ngRoute', 'ngSanitize'],
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

app.run(($rootScope) =>
	{
		$rootScope.settings = {
			use_idolized_thumbnails : getStorage('use_idolized_thumbnails', true),
			order_reversed          : getStorage('order_reversed', false),
			highlight_source        : getStorage('highlight_source', '0'),
			show_tooltips           : getStorage('show_tooltips', true),
			collapsed               : getStorage('collapsed', false),
			hide_empty_rows         : getStorage('hide_empty_rows', false),
			// alt           : true,
		}
		
		$rootScope.disable_scrolling = false;
		$rootScope.scrollDisabler = () =>
		{
			if ($rootScope.disable_scrolling)
			{
				return 'scrolling-disabled';
			}
			return '';
		}
	}
)

app.controller('BaseController', function($rootScope, $scope, $route, $routeParams, $location, $timeout, $parse)
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
			let allowed_keys = ['filter', 'filter_featured', 'filter_highlight'];
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
				$event.target == $event.target.closest('#side-nav'))
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
			
			let parent = element.closest('.event-title');
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

let toggleTooltip = function($scope, $event, visible)
{
	$scope.display_tooltip = visible;
	let tooltip = document.querySelector("#card-tooltip");
	if (!visible)
	{
		tooltip.style.visibility = 'hidden';
		tooltip.style.top = '-999px';
		tooltip.style.left = '-999px';
		tooltip.style.right = 'auto';
		return;
	}
	
	tooltip.style.visibility = 'visible';
	
	let e = $event.target.closest('.tooltip-data');
	
	const keys = [
		'member-id', 'member-name',
		'card-status',
		'card-attribute', 'card-type',
		'card-title-normal', 'card-title-idolized',
		'card-source', 'card-release-date',
		'card-event',
	];
	
	$scope.tooltip_data = Object.assign(...keys.flatMap((key) => {
		return {
			[key.replace(/-/g, '_')] : e.getAttribute('data-' + key)
		}
	}));
	if (!$scope.tooltip_data.card_status)
		$scope.tooltip_data.card_status = 1;
	
	let rect = e.getBoundingClientRect();
	
	const doc = document.documentElement;
	const view_width = doc.clientWidth;
	const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
	
	const flipAnchor = (rect.x > view_width * 0.66);
	
	const offset = ($scope.tooltip_data.card_status == 1 ? 
		{x: 15, y: -16} :
		{x: 15, y: -4}
	);
	
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

const MEMBERS_ORDERED = [
	{ id: -1,  name: "— Show All —",      group: undefined },
	{ id: 8,   name: "Hanayo Koizumi",    group: "µ's" },
	{ id: 5,   name: "Rin Hoshizora",     group: "µ's" },
	{ id: 6,   name: "Maki Nishikino",    group: "µ's" },
	{ id: 1,   name: "Honoka Kousaka",    group: "µ's" },
	{ id: 3,   name: "Kotori Minami",     group: "µ's" },
	{ id: 4,   name: "Umi Sonoda",        group: "µ's" },
	{ id: 7,   name: "Nozomi Toujou",     group: "µ's" },
	{ id: 2,   name: "Eli Ayase",         group: "µ's" },
	{ id: 9,   name: "Nico Yazawa",       group: "µ's" },
	{ id: 107, name: "Hanamaru Kunikida", group: "Aqours" },
	{ id: 106, name: "Yoshiko Tsushima",  group: "Aqours" },
	{ id: 109, name: "Ruby Kurosawa",     group: "Aqours" },
	{ id: 101, name: "Chika Takami",      group: "Aqours" },
	{ id: 102, name: "Riko Sakurauchi",   group: "Aqours" },
	{ id: 105, name: "You Watanabe",      group: "Aqours" },
	{ id: 103, name: "Kanan Matsuura",    group: "Aqours" },
	{ id: 104, name: "Dia Kurosawa",      group: "Aqours" },
	{ id: 108, name: "Mari Ohara",        group: "Aqours" },
	{ id: 209, name: "Rina Tennouji",     group: "Nijigasaki" },
	{ id: 202, name: "Kasumi Nakasu",     group: "Nijigasaki" },
	{ id: 203, name: "Shizuku Ousaka",    group: "Nijigasaki" },
	{ id: 210, name: "Shioriko Mifune",   group: "Nijigasaki" },
	{ id: 201, name: "Ayumu Uehara",      group: "Nijigasaki" },
	{ id: 207, name: "Setsuna Yuuki",     group: "Nijigasaki" },
	{ id: 205, name: "Ai Miyashita",      group: "Nijigasaki" },
	{ id: 212, name: "Lanzhu Zhong",      group: "Nijigasaki" },
	{ id: 208, name: "Emma Verde",        group: "Nijigasaki" },
	{ id: 206, name: "Kanata Konoe",      group: "Nijigasaki" },
	{ id: 204, name: "Karin Asaka",       group: "Nijigasaki" },
	{ id: 211, name: "Mia Taylor",        group: "Nijigasaki" },
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
		
		$scope.toggleTooltip = ($event, visible) => { toggleTooltip($scope, $event, visible); }
		
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
			{ id: 4,  title: 'Other'     },
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
				output.push('filtering-active');
				// output.push('filtering-by-banner');
				output.push('show-banner-' + $scope.filter_settings.banner);
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
		
		$scope.toggleTooltip = ($event, visible) => { toggleTooltip($scope, $event, visible); }
		
		$scope.loading = false;
	}
);

app.controller('MainController', function($rootScope, $scope, $route, $routeParams, $location)
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
		
		$scope.toggleTooltip = ($event, visible) => { toggleTooltip($scope, $event, visible); }
		
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

app.controller('StatsController', function($rootScope, $scope, $route, $routeParams, $location, $timeout)
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
		// templateUrl: 'tooltip.html',
		template: '<div class="card-tooltip-inner" ng-class="\'idol-\' + data.member_id"><div class="member-info idol-bg-color-dark idol-bg-glow-border"><div class="name">[[ data.member_name ]]</div><div class="card-info" ng-if="data.card_status == 1"><span class="icon-32" ng-class="\'attribute-\' + data.card_attribute"></span><span class="icon-32" ng-class="\'type-\' + data.card_type"></span></div></div><table class="card-details" ng-if="data.card_status == 1"><colgroup><col style="min-width: 10rem"><col></colgroup><tr class="card-title"><td colspan="2">&#12300;<span class="normal">[[ data.card_title_normal ]]</span><span class="idolized">[[ data.card_title_idolized ]]</span>&#12301;</td></tr><tr><th>Debuted</th><td>[[ data.card_source ]]</td></tr><tr ng-if="data.card_event"><th>Related Event</th><td>[[ data.card_event ]]</td></tr><tr><th>Release Date (JP)</th><td>[[ data.card_release_date ]]</td></tr></table><div class="card-details" ng-if="data.card_status == 2"><b>[[ first_name ]]</b> has yet to receive a card in this cycle.</div><div class="card-details" ng-if="data.card_status == 3"><b>[[ first_name ]]</b> did not receive a card in this cycle.</div></div>',
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
