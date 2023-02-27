
app.config(($interpolateProvider, $routeProvider, $locationProvider, SiteSettingsProvider, SiteRoutesProvider) =>
{
	$interpolateProvider.startSymbol('[[');
	$interpolateProvider.endSymbol(']]');
	
	SiteRoutesProvider.register_route(
	{
		title       : 'Home',
		path        : '/',
		controller  : 'MainController',
		template    : 'home.html',
	});
	
	for (const route of SiteRoutesProvider.routes())
	{
		$routeProvider.when(route.path, {
			controller:  route.controller,
			templateUrl: function(routeParams)
			{
				if (typeof route.template == "function")
				{
					let page_path = route.template(routeParams);
					if (page_path !== false)
					{
						return Utility.cache_buster('pages/' + page_path, BUILD_ID);
					}
					else
					{
						return false;
					}
				}
				
				return Utility.cache_buster('pages/' + route.template, BUILD_ID);
			},
			reloadOnSearch: route.reload || false,
			redirectTo : function(routeParams, locationPath, locationParams)
			{
				if (typeof route.template == "function")
				{
					let page_path = route.template(routeParams);
					if (page_path === false)
					{
						return route.error_redirect;
					}
				}
			},
		})
	}

	$routeProvider.otherwise({
		redirectTo: '/',
	});

	$locationProvider.hashPrefix('');
	// $locationProvider.html5Mode(true);
})


app.run(($rootScope, $window, $templateCache, $http, RouteEvent, SiteSettings) =>
{
	$rootScope.settings = SiteSettings.saved_settings;
	
	$rootScope.RouteEvent = RouteEvent;
	
	$rootScope.mobile_mode = Utility.mobile_mode;
	$rootScope.prefers_reduced_motion = Utility.prefers_reduced_motion;
	
	$rootScope.disable_scrolling = false;
	$rootScope.scrollDisabler = () =>
	{
		if ($rootScope.disable_scrolling)
		{
			return 'scrolling-disabled';
		}
		return '';
	}
	
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
		console.log(timestamp, label);
		
		const text = `Next ${label} preview ${approximate ? 'approximately ' : ''}<t:${timestamp}:R> on <t:${timestamp}:F>`;
		console.log(text);
		
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

