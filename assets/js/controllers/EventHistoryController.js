
app.config(function(SiteSettingsProvider, SiteRoutesProvider)
{
	SiteRoutesProvider.register_route(
	{
		title        : 'Event History',
		path         : '/event_history',
		controller   : 'EventHistoryController',
		template     : 'event_history.html',
		allowed_keys : ['filter', 'filter_featured', 'filter_highlight'],
	});
});

app.controller('EventHistoryController', function($rootScope, $scope, $route, $routeParams, $window, RouteEvent, LocationKeys)
	{
		$scope.loading = true;
		
		$scope.filter_settings = {
			highlight     : false,
			featured_only : false,
		};
		
		$scope.filter_index = 0;
		$scope.filter_member = false;
		
		$scope.$watch('filter_member', (member) =>
		{
			if (member instanceof Member)
			{
				LocationKeys.set('filter', member.first_name.toLowerCase());
			}
			else
			{
				LocationKeys.reset('filter');
			}
			$scope.$broadcast('refresh-deferred-loads');
		});
		
		const url_options = LocationKeys.get();
		if (url_options.filter !== undefined)
		{
			let filter_name = url_options.filter.toLowerCase().trim();
			for (let i = 0; i < Member.members_ordered.length; i++)
			{
				let first_name = Member.members_ordered[i].first_name.toLowerCase();
				if (first_name === filter_name)
				{
					$scope.filter_index = i + 1;
					$scope.filter_member = Member.members_ordered[i];
					break;
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
			
			if ($scope.filter_member instanceof Member)
			{
				output.push('filtering-active');
				output.push('show-idol-' + $scope.filter_member.id);
				
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
				LocationKeys.set('filter_featured', 'true');
			}
			else
			{
				LocationKeys.reset('filter_featured');
			}
			
			if ($scope.filter_settings.highlight)
			{
				LocationKeys.set('filter_highlight', 'true');
			}
			else
			{
				LocationKeys.reset('filter_highlight');
			}
			$scope.$broadcast('refresh-deferred-loads');
		}, true);
		
		$scope.$watch('$root.settings.order_reversed', function(new_reversed, old_reversed)
		{
			if (new_reversed == old_reversed) return;
			$scope.$broadcast('refresh-deferred-loads');
		});
		
		$scope.$on('keydown', (_, e) =>
		{
			if (e.repeat || e.ctrlKey || e.altKey || e.metaKey) return;
			
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
					$scope.filter_member = false;
					$scope.filter_index = 0;
					
					$scope.filter_settings.highlight     = false;
					$scope.filter_settings.featured_only = false;
					return;
				}
			}
		});
		
		$scope.loading = false;
	}
);
