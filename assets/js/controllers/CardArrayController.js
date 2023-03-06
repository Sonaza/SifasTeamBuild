
app.config(function(SiteSettingsProvider, SiteRoutesProvider)
{
	const numbered_page_subtitle = function(routeParams, locationSearch)
	{
		const page = Number(locationSearch.page) || 1;
		return `Page ${page}`;
	}
	
	SiteRoutesProvider.register_route(
	{
		title        : 'µ\'s Cards',
		path         : '/muse/:page?',
		controller   : 'CardArrayController',
		template     : 'idol_arrays_muse.html',
		subtitle     : numbered_page_subtitle,
		allowed_keys : ['page'],
	})
	.register_route(
	{
		title        : 'Aqours Cards',
		path         : '/aqours/:page?',
		controller   : 'CardArrayController',
		template     : 'idol_arrays_aqours.html',
		subtitle     : numbered_page_subtitle,
		allowed_keys : ['page'],
	})
	.register_route(
	{
		title        : 'Nijigasaki Cards',
		path         : '/nijigasaki/:page?',
		controller   : 'CardArrayController',
		template     : 'idol_arrays_nijigasaki.html',
		subtitle     : numbered_page_subtitle,
		allowed_keys : ['page'],
	});
});


app.controller('CardArrayController', function($rootScope, $scope, $route, $routeParams, $timeout, LocationKeys)
{
	$scope.loading = true;
	
	let find_number_of_pages = () =>
	{
		const page_selector = document.querySelector('.array-group-page-selector');
		if (page_selector)
		{
			return parseInt(page_selector.getAttribute('data-num-pages'));
		}
		console.error("Couldn't find number of array pages");
		return 1;
	}
	
	const num_pages = find_number_of_pages();
	const current_page = LocationKeys.get('page');
	
	if (current_page === undefined && $routeParams.page !== undefined)
	{
		const old_page_number = Number($routeParams.page);
		if (!isNaN(old_page_number))
		{
			LocationKeys.set('page', Math.min(num_pages, old_page_number + 1));
			$route.updateParams({'page': undefined});
			return;
		}
	}
	
	$rootScope.$on("$routeChangeStart", function($event, next_route, current_route)
	{
		LocationKeys.reset('page');
	});
	
	$scope.set_page = (page_number, $event) =>
	{
		$scope.active_page = Math.min(num_pages, page_number);
		LocationKeys.set('page', $scope.active_page);
		
		if ($event !== undefined)
		{
			$event.preventDefault();
		}
	}
	
	$scope.set_page(current_page || 1);
	
	$scope.page_active_class = (page) =>
	{
		if ($scope.active_page == page || ($scope.active_page === undefined && page == 1))
		{
			return 'active';
		}
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
					$scope.set_page(number);
					e.preventDefault();
				}
				return;
			}
		}
	});

	$scope.loading = false;
});
