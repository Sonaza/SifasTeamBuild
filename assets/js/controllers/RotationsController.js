
app.config(function(SiteSettingsProvider, SiteRoutesProvider)
{
	SiteRoutesProvider.register_route(
	{
		title       : 'UR Rotations',
		path        : '/ur-rotations',
		controller  : 'RotationsController',
		template    : 'ur_rotations.html',
	})
	.register_route(
	{
		title       : 'SR Sets',
		path        : '/sr-sets',
		controller  : 'RotationsController',
		template    : 'sr_sets.html',
	})
	.register_route(
	{
		title       : 'Festival Rotations',
		path        : '/festival',
		controller  : 'RotationsController',
		template    : 'festival_rotations.html',
	})
	.register_route(
	{
		title       : 'Party Rotations',
		path        : '/party',
		controller  : 'RotationsController',
		template    : 'party_rotations.html',
	})
	.register_route(
	{
		title       : 'Event Rotations',
		path        : '/events',
		controller  : 'RotationsController',
		template    : 'event_rotations.html',
	})
});


app.controller('RotationsController', function($rootScope, $scope, $route, $routeParams,
	$location, $window, LocationKeys, RouteEvent)
{
	$scope.loading = true;
	
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
	
	$scope.loading = false;
});
