
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

const site_title = "SIFAS Card Rotations";

const routes = [
	{ title : 'UR Rotations',       basepath: '/ur-rotations', path: '/ur-rotations',      controller: 'MainController',  template: 'ur_rotations.html',           },
	{ title : 'µ\'s Cards',         basepath: '/muse',         path: '/muse/:page?',       controller: 'MainController',  template: 'idol_arrays_muse.html',       },
	{ title : 'Aqours Cards',       basepath: '/aqours',       path: '/aqours/:page?',     controller: 'MainController',  template: 'idol_arrays_aqours.html',     },
	{ title : 'Nijigasaki Cards',   basepath: '/nijigasaki',   path: '/nijigasaki/:page?', controller: 'MainController',  template: 'idol_arrays_nijigasaki.html', },
	{ title : 'Festival Rotations', basepath: '/festival',     path: '/festival',          controller: 'MainController',  template: 'festival_rotations.html',     },
	{ title : 'Party Rotations',    basepath: '/party',        path: '/party',             controller: 'MainController',  template: 'party_rotations.html',        },
	{ title : 'Event Rotations',    basepath: '/event',        path: '/event',             controller: 'MainController',  template: 'event_rotations.html',        },
	{ title : 'SR Sets',            basepath: '/sr-sets',      path: '/sr-sets',           controller: 'MainController',  template: 'sr_sets.html',                },
	{ title : 'Card Stats',         basepath: '/stats',        path: '/stats/:page?',      controller: 'StatsController', template: 'stats.html',                  },
];

const stats_subpages = {
	'general'   : "General",
	'event'     : "Event URs",
	'festival'  : "Festival URs",
	'party'     : "Party URs",
	'spotlight' : "Party + Spotlight",
	'limited'   : "Festival + Party",
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
.config(['$routeProvider', '$locationProvider',
	function($routeProvider, $locationProvider)
	{
		$routeProvider.when('/', {
			controller:  'MainController',
			templateUrl: 'pages/main.html',
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
])

.controller('NavController', ['$rootScope', '$scope', '$routeParams', '$location',
	function($rootScope, $scope, $routeParams, $location)
	{
		$scope.isActive = function(viewLocation, exact_match)
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

		$scope.classActive = function(viewLocation, exact_match)
		{
			if ($scope.isActive(viewLocation, exact_match))
			{
				return 'active';
			}
		}
		
		$scope.$on('update-title', function(nonsense, sub_title)
		{
			if ($location.path() == '/')
			{
				$rootScope.title = site_title;
			}
			else
			{
				for (const route of routes)
				{
					if ($scope.isActive(route['basepath']))
					{
						$rootScope.title = route['title'] + " / " + sub_title + " &mdash; " + site_title;
						break;
					}
				}
			}
		})
		
	}
])

.controller('MainController', ['$rootScope', '$scope', '$routeParams', '$location',
	function($rootScope, $scope, $routeParams, $location)
	{
		$scope.loading = true;
		
		$scope.settings = {
			use_idolized_thumbnails : true,
			order_reversed          : false,
		};
		
		$scope.active_page = $routeParams.page;
		if ($scope.active_page === undefined)
		{
			$scope.active_page = 0;
		}
		
		$scope.isActive = function(page)
		{
			return $scope.active_page == page;
		}
		
		$scope.pageActive = function(page)
		{
			if ($scope.isActive(page))
			{
				return 'active';
			}
		}
		
		let page_subtitle = "Page " + (parseInt($scope.active_page) + 1);
		$rootScope.$broadcast('update-title', page_subtitle);
		
		$scope.loading = false;
		
		window.scrollTo(0, 0);
		
		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
])

.controller('StatsController', ['$rootScope', '$scope', '$routeParams', '$location',
	function($rootScope, $scope, $routeParams, $location)
	{
		$scope.loading = true;
		
		$scope.active_page = $routeParams.page;
		if ($scope.active_page === undefined)
		{
			$scope.active_page = 'general';
		}
		
		$scope.isActive = function(page)
		{
			return $scope.active_page == page;
		}
		
		$scope.pageActive = function(page)
		{
			if ($scope.isActive(page))
			{
				return 'active';
			}
		}
		
		$scope.get_subtitle = function(page)
		{
			if (stats_subpages[page])
			{
				return stats_subpages[page];
			}
			return "";
		}
		
		let page_subtitle = $scope.get_subtitle($scope.active_page);
		$rootScope.$broadcast('update-title', page_subtitle);
		
		$scope.loading = false;
		
		window.scrollTo(0, 0);
		
		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
])

.directive('pillButton', ['$parse', function ($parse)
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
}])
