
app.config(($interpolateProvider, $routeProvider, $locationProvider, SiteSettingsProvider, SiteRoutesProvider) =>
{
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
	
	SiteRoutesProvider.configure_route_provider();

	$locationProvider.hashPrefix('');
	$locationProvider.html5Mode(true);
})


app.run(($rootScope, $window, $templateCache, $http, RouteEvent, SiteSettings) =>
{
	$rootScope.settings = SiteSettings.saved_settings;
	
	$rootScope.RouteEvent = RouteEvent;
	
	$rootScope.mobile_mode = Utility.mobile_mode;
	$rootScope.prefers_reduced_motion = Utility.prefers_reduced_motion;
	
	$rootScope.openMobileTooltip = ($event) =>
	{
		if (!Utility.mobile_mode() || !$rootScope.settings.show_tooltips)
		{
			return;
		}
		
		$rootScope.toggleTooltip($event, true);
		$event.preventDefault();
	}
	
	$rootScope.dismissMobileTooltip = ($event) =>
	{
		if (!Utility.mobile_mode())
		{
			return;
		}
		
		$rootScope.toggleTooltip($event, false);
	}
	
	$rootScope.copy_discord_timestamp = ($event, timestamp, approximate) =>
	{
		const el = document.querySelector("#countdown-label-" + timestamp);
		if (el === null)
			return;
		
		const label = el.innerHTML.trim();
		const text = `Next ${label} preview ${approximate ? 'approximately ' : ''}<t:${timestamp}:R> on <t:${timestamp}:F>`;
		
		Utility.copy_to_clipboard(text)
			.then(() =>
			{
				const button = $event.target.closest('button');
				button.classList.add("copied");
				
				setTimeout(() =>
				{
					button.classList.remove("copied");
				}, 1500);
			})
			.catch((error) =>
			{
				console.error('Error copying text: ', error);
			});
	}
	
	$rootScope.toggleTooltip = ($event, visible) => { CardTooltip.toggleTooltip($rootScope, $event, visible); }
	angular.element($window).on('resize', () => { $rootScope.toggleTooltip(undefined, false); });
})

