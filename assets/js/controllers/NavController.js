
app.controller('NavController', function($rootScope, $scope, $routeParams, $location, SiteRoutes)
	{
		$scope.classActive = (page_path) =>
		{
			const active_route = SiteRoutes.active_route();
			if (active_route.id == page_path.substr(1))
			{
				return 'active';
			}
		}
	}
)
