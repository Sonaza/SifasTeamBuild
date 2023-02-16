
const stats_subpages = {
	'general'     : "General",
	'overdueness' : "Overdueness",
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

app.config(function(SiteSettingsProvider, SiteRoutesProvider)
{
	SiteRoutesProvider.register_route(
	{
		title       : 'Card Stats',
		path        : '/stats/:page?',
		controller  : 'CardStatsController',
		template    : function(routeParams)
		{
			if (routeParams.page !== undefined && routeParams.page in this.subpages)
			{
				if (routeParams.page != 'general')
				{
					return 'stats_' + routeParams.page + '.html';
				}
			}
			else if (routeParams.page === undefined || routeParams.page === 'general')
			{	
				return 'stats.html';
			}
			
			return false;
		},
		error_redirect : '/stats',
		subpages          : {
			'general'     : "General",
			'overdueness' : "Overdueness",
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
		},
		subtitle          : ['page', 'general'],
	});
});

app.controller('CardStatsController', function($rootScope, $scope, $route, $routeParams, $location, $timeout, $window)
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

		$scope.loading = false;

		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
)
