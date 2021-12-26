
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

function load_params()
{
	let params;

	if (storageAvailable('localStorage'))
	{
		let paramsData = window.localStorage.getItem('params');

		if (paramsData && typeof paramsData == "string")
			paramsData = JSON.parse(paramsData);

		if (!paramsData || !Number.isInteger(paramsData.version) || paramsData.version < defaultParams.version)
		{
			console.log("RESETTING PARAMS");
			params = JSON.parse(JSON.stringify(defaultParams));
		}
		else
		{
			console.log("LOADING PARAMS");
			params = paramsData;
		}
	}
	else
	{
		console.log("STORAGE NOT AVAILABEL!");
		params = JSON.parse(JSON.stringify(defaultParams));
	}

	return params;
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
	{ 'value' : 0,         'label' : 'No Highlighting' },
	{ 'value' : 1,         'label' : 'Initial Cards' },
	{ 'value' : 2,         'label' : 'Events & SBL' },
	{ 'value' : 3,         'label' : 'Gacha' },
	{ 'value' : 5,         'label' : 'Spotlight ' },
	{ 'value' : 6,         'label' : 'Festival' },
	{ 'value' : 7,         'label' : 'Party' },
	{ 'value' : 'gacha',   'label' : 'Any Gacha' },
	{ 'value' : 'limited', 'label' : 'Any Limited' },
]

let getStorage = (key, default_value) =>
{
	let value = window.localStorage.getItem(key);
	if (value === null)
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
			highlight_source        : getStorage('highlight_source', 0),
			show_tooltips           : getStorage('show_tooltips', true),
		}
	}
)

app.controller('BaseController', function($rootScope, $scope, $route, $routeParams, $location)
	{
		$scope.highlight_options = highlight_options;
		$scope.active_settings = () =>
		{
			let output = [];
			
			if ($rootScope.settings.use_idolized_thumbnails)
			{
				output.push('use-idolized-thumbnails');
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
			if ($rootScope.settings.highlight_source == 0)
			{
				output.push('source-highlighting-inactive');
			}
			else if ($rootScope.settings.highlight_source != 0)
			{
				output.push('source-highlighting-active');
			}
			
			return output.join(' ');
		}
		
		$scope.$watch('$root.settings', function(bs, settings)
		{
			saveStorage($rootScope.settings);
		}, true);
		
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
		  				$rootScope.settings.highlight_source        = 0;
		  				return;
		  			}
	  			}
			}
			
			$rootScope.$broadcast('keydown', $event);
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

		let page_subtitle = $scope.get_subtitle($scope.active_page);
		$rootScope.$broadcast('update-title', page_subtitle);

		$scope.loading = false;

		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
)

app.directive('pillButton', function($parse)
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
					angular.element(element).addClass('active');
				}
				else
				{
					angular.element(element).removeClass('active');
				}
			});
		}
	}
})

app.directive('cardTooltip', function($parse)
{
	return {
		restrict: 'A',
		templateUrl: 'tooltip.html',
		link: function (scope, element, attrs)
		{
			// let lol = $parse(attrs.cardTooltip)(scope);
			scope.$watch(attrs.cardTooltip, function(value)
			{
				scope.data = value;
				scope.first_name = value.member_name.split(' ')[0];
			}, true);
		}
	}
})

