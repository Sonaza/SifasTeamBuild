
app.config(function(SiteSettingsProvider, SiteRoutesProvider)
{
	SiteRoutesProvider.register_route(
	{
		title        : 'Banner History',
		path         : '/banners',
		controller   : 'BannersController',
		template     : 'banners.html',
		allowed_keys : ['filter', 'filter_highlight', 'banner'],
	});
});

app.controller('BannersController', function($rootScope, $scope, $route, $routeParams, $window, RouteEvent, LocationKeys)
	{
		$scope.loading = true;
		
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
			banner        : -1,
			highlight     : false,
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
		if (url_options.banner !== undefined)
		{
			let filter_string = url_options.banner.toLowerCase().trim();
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
			
			if ($scope.filter_member instanceof Member)
			{
				output.push('filtering-active');
				output.push('show-idol-' + $scope.filter_member.id);
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
				LocationKeys.set('filter_highlight', 'true');
			}
			else
			{
				LocationKeys.reset('filter_highlight');
			}
			$scope.$broadcast('refresh-deferred-loads');
		}, true);
		
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
						LocationKeys.set('banner', type_title);
					}
					else
					{
						LocationKeys.reset('banner');
					}
					
					break;
				}
			}
			$scope.$broadcast('refresh-deferred-loads');
		});
		
		$scope.$watch('$root.settings.order_reversed', function(new_reversed, old_reversed)
		{
			if (new_reversed == old_reversed) return;
			$scope.$broadcast('refresh-deferred-loads');
		});
		
		$scope.$on('keydown', (_, e) =>
		{
			if (e.repeat || e.ctrlKey || e.altKey || e.metaKey) return;
			
			if (e.keyCode == 66) // B-key
			{
				e.preventDefault();
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
					$scope.filter_member = false;
					$scope.filter_index = 0;
					
					$scope.filter_settings.banner     = -1;
					$scope.filter_settings.highlight  = false;
					return;
				}
			}
		});
		
		$scope.loading = false;
	}
);
