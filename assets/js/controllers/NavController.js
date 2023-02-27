
app.controller('NavController', function($rootScope, $scope, $routeParams, $location, SiteRoutes)
	{
		$scope.classActive = (page_path) =>
		{
			const active_route = SiteRoutes.active_route();
			if (active_route.path_matches_current(page_path))
			{
				return 'active';
			}
		}
	}
)
