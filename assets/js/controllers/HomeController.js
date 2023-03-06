
app.config(function(SiteRoutesProvider)
{
	SiteRoutesProvider.register_route(
	{
		title       : 'Home',
		path        : '/',
		controller  : 'HomeController',
		template    : 'home.html',
	});
});

app.controller('HomeController', function($scope)
{
	$scope.loading = false;
});
