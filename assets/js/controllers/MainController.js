
app.config(function(SiteSettingsProvider, SiteRoutesProvider)
{
	const numbered_page_subtitle = function(routeParams)
	{
		let page = parseInt(routeParams.page);
		if (isNaN(page))
			page = 0;
		return "Page " + (page + 1);
	}
	
	SiteRoutesProvider.register_route(
	{
		title       : 'UR Rotations',
		path        : '/ur-rotations',
		controller  : 'MainController',
		template    : 'ur_rotations.html',
	})
	.register_route(
	{
		title       : 'SR Sets',
		path        : '/sr-sets',
		controller  : 'MainController',
		template    : 'sr_sets.html',
	})
	.register_route(
	{
		title       : 'Festival Rotations',
		path        : '/festival',
		controller  : 'MainController',
		template    : 'festival_rotations.html',
	})
	.register_route(
	{
		title       : 'Party Rotations',
		path        : '/party',
		controller  : 'MainController',
		template    : 'party_rotations.html',
	})
	.register_route(
	{
		title       : 'Event Rotations',
		path        : '/events',
		controller  : 'MainController',
		template    : 'event_rotations.html',
	})
	.register_route(
	{
		title        : 'µ\'s Cards',
		path         : '/muse/:page?',
		controller   : 'MainController',
		template     : 'idol_arrays_muse.html',
		subtitle     : numbered_page_subtitle,
	})
	.register_route(
	{
		title        : 'Aqours Cards',
		path         : '/aqours/:page?',
		controller   : 'MainController',
		template     : 'idol_arrays_aqours.html',
		subtitle     : numbered_page_subtitle,
	})
	.register_route(
	{
		title        : 'Nijigasaki Cards',
		path         : '/nijigasaki/:page?',
		controller   : 'MainController',
		template     : 'idol_arrays_nijigasaki.html',
		subtitle     : numbered_page_subtitle,
	});
});

app.controller('MainController', function($rootScope, $scope, $route, $routeParams, $location, $window, RouteEvent)
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
		
		const column_wrapper_element = document.querySelector('.rotation-column-wrapper');
		if (column_wrapper_element)
		{
			RouteEvent.element(column_wrapper_element).on('scroll', ($event) =>
			{
				$scope.$broadcast('refresh-deferred-loads');
			});
		}
		
		$scope.$watch('$root.settings.order_reversed', function(new_reversed, old_reversed)
		{
			if (new_reversed == old_reversed) return;
			$scope.$broadcast('refresh-deferred-loads');
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

		$scope.loading = false;

		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
)
