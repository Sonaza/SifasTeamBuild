
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

const routes = [
	{
		title       : 'UR Rotations',
		path        : '/ur-rotations',
		controller  : 'MainController',
		template    : 'ur_rotations.html',
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
		template    : 'stats.html',
		hasSubpages : true,
	},
];

const stats_subpages = {
	'general'   : "General",
	'event'     : "Event URs",
	'festival'  : "Festival URs",
	'party'     : "Party URs",
	'limited'   : "Festival + Party",
	'spotlight' : "Party + Spotlight",
	'gacha'     : "Any Gacha UR",
	'ur'        : "Any UR",
	'sr'        : "Any SR",
};

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
			$routeProvider.when(route['path'], {
				controller:  route['controller'],
				templateUrl: 'pages/' + route['template'],
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
	{ 'value' : '0',       'label' : 'No Highlighting' },
	{ 'value' : '1',       'label' : 'Initial Cards' },
	{ 'value' : '2',       'label' : 'Events & SBL' },
	{ 'value' : '3',       'label' : 'Gacha' },
	{ 'value' : '5',       'label' : 'Spotlight ' },
	{ 'value' : '6',       'label' : 'Festival' },
	{ 'value' : '7',       'label' : 'Party' },
	{ 'value' : 'gacha',   'label' : 'Any Gacha' },
	{ 'value' : 'limited', 'label' : 'Any Limited' },
];

const highlight_map = {
	'none'      : '0',
	'initial'   : '1',
	'event'     : '2',
	'gacha'     : '3',
	'spotlight' : '5',
	'festival'  : '6',
	'party'     : '7',
	'any_gacha' : 'gacha',
	'limited'   : 'limited',
};

const highlight_reverse_map = {
	'0'       : 'none',
	'1'       : 'initial',
	'2'       : 'event',
	'3'       : 'gacha',
	'5'       : 'spotlight',
	'6'       : 'festival',
	'7'       : 'party',
	'gacha'   : 'any_gacha',
	'limited' : 'limited',
};

let getStorage = (key, default_value) =>
{
	if (!storageAvailable('localStorage'))
		return default_value;
	
	let value = window.localStorage.getItem(key);
	if (value === null || value === "null")
		return default_value;
	
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
			alt           : true,
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
			console.log(highlight_map, url_options.highlight in highlight_map);
			
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
		
		//////////////////////////////////////////////////
		
		$scope.highlight_options = highlight_options;
		$scope.active_settings = () =>
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
			
			if ($rootScope.settings.order_reversed)
			{
				output.push('order-reversed');
			}
			
			if (!$rootScope.settings.show_tooltips)
			{
				output.push('hide-tooltips');
			}
			
			output.push('source-highlight-' + $rootScope.settings.highlight_source);
			if ($rootScope.settings.highlight_source == 0)
			{
				output.push('source-highlighting-inactive');
			}
			else if ($rootScope.settings.highlight_source != 0)
			{
				output.push('source-highlighting-active');
			}
			
			if ($scope.navigation_visible || $scope.settings_visible)
			{
				output.push('sidebar-open');
			}
			
			return output.join(' ');
		}
		
		$scope.$watch('$root.settings', function(bs, settings)
		{
			saveStorage($rootScope.settings);
			$timeout(() => {
				$scope.unfocus();
			}, 350);
			
			$location.search('highlight', highlight_reverse_map[$rootScope.settings.highlight_source]);
			// $location.search('idolized', $rootScope.settings.use_idolized_thumbnails ? 'true' : 'false');
			// $location.search('reverse', $rootScope.settings.order_reversed ? 'true' : 'false');
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
		
		$rootScope.$on("$locationChangeStart", function(event, next, current)
		{ 
			$scope.unfocus();
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
						return;
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
					
					if ($scope.isActive(basepath))
					{
						if (route.hasSubpages)
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
		
		$scope.toggleTooltip = function($event, show)
		{
			$scope.display_tooltip = show;
			let tooltip = document.querySelector("#card-tooltip");
			if (!show)
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
		link: function (scope, element, attrs)
		{
			element.on('click', function(event)
			{
				event.preventDefault();
				$parse(attrs.pillButton).assign(scope, !$parse(attrs.pillButton)(scope));
				scope.$apply();
			});

			scope.$watch(attrs.pillButton, function(value)
			{
				if (value)
				{
					angular.element(element).addClass('active').addClass('changed');
				}
				else
				{
					angular.element(element).removeClass('active');
				}
				
				angular.element(element).addClass('changed');
				$timeout(() => {
					angular.element(element).removeClass('changed');
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
		template: '<div class="card-tooltip-inner" ng-class="\'idol-\' + data.member_id"><div class="member-info idol-bg-color-dark idol-bg-glow-border"><div class="name">[[ data.member_name]]</div><div class="card-info" ng-if="data.card_status==1"><span class="icon-32" ng-class="\'attribute-\' + data.card_attribute"></span><span class="icon-32" ng-class="\'type-\' + data.card_type"></span></div></div><table class="card-details" ng-if="data.card_status==1"><colgroup><col style="min-width: 10rem"><col></colgroup><tr class="card-title"><td colspan="2">&#12300;<span class="normal">[[ data.card_title_normal]]</span><span class="idolized">[[ data.card_title_idolized]]</span>&#12301;</td></tr><tr><th>Debuted</th><td>[[ data.card_source]]</td></tr><tr><th>Release Date (JP)</th><td>[[ data.card_release_date]]</td></tr></table><div class="card-details" ng-if="data.card_status==2"><b>[[ first_name]]</b> has yet to receive a card in this cycle.</div><div class="card-details" ng-if="data.card_status==3"><b>[[ first_name]]</b> did not receive a card in this cycle.</div></div>',
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
