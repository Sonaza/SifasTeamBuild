
const history_subpages = {
	'all'         : "All",
	'event'       : "Event URs",
	'festival'    : "Festival URs",
	'party'       : "Party URs",
	'limited'     : "Limited URs",
	'nonlimited'  : "Non-Limited Gacha UR",
	'gacha'       : "Any Gacha UR",
	'ur'          : "Any UR",
	'sr'          : "Any SR",
};

app.config(function(SiteSettingsProvider, SiteRoutesProvider)
{
	SiteRoutesProvider.register_route(
	{
		title       : 'Card History',
		path        : '/history/:idol?/:page?',
		controller  : 'HistoryController',
		template    : function(routeParams)
		{
			if (routeParams.idol !== undefined && routeParams.idol in Member.members_by_name)
			{
				if (routeParams.page in this.subpages)
				{
					return 'history/history_' + routeParams.idol + '_' + routeParams.page + '.html';
				}
				else
				{
					return 'history/history_' + routeParams.idol + '_all.html';
				}
			}
			else if (routeParams.idol === undefined)
			{	
				return 'history.html';
			}
			
			return false;
		},
		error_redirect : '/history',
		subpages       : {
			'all'         : "All",
			'event'       : "Event URs",
			'festival'    : "Festival URs",
			'party'       : "Party URs",
			'limited'     : "Limited URs",
			'nonlimited'  : "Non-Limited Gacha UR",
			'gacha'       : "Any Gacha UR",
			'ur'          : "Any UR",
			'sr'          : "Any SR",
		},
		subtitle          : function(routeParams)
		{
			if (routeParams.idol)
			{
				// const subpage_title = this.subpages[routeParams.page] || this.subpages['all'];
				// return Member.members_by_name[routeParams.idol].first_name + " " + subpage_title;
				return Member.members_by_name[routeParams.idol].first_name;
			}
			return undefined;
		},
	});
});

app.controller('HistoryController', function($rootScope, $scope, $route, $routeParams, $location, $timeout, $window)
	{
		$scope.loading = true;
		
		if ($routeParams.page === undefined)
		{
			window.scrollTo(0, 0);
		}
		
		$scope.getIdolGroup = (idol) =>
		{
			for (const member of Member.members_ordered)
			{
				if (member.id <= 0)
					continue;
				
				let first_name = member.first_name.toLowerCase();
				if (first_name == idol)
				{
					return member.group.tag;
				}
			}
			return false;
		}
			
		$scope.idol_navigation = {
			'group'	     : $scope.getIdolGroup($routeParams.idol),
			'idol'       : $routeParams.idol,
			'idol_group' : $scope.getIdolGroup($routeParams.idol),
		};
		
		$scope.setGroup = (group) => 
		{
			$scope.idol_navigation.group = group;
			
			if (group == $scope.idol_navigation.idol_group)
			{
				setTimeout($scope.scrollPageSelectors);
			}
		}
		
		$scope.active_page = $routeParams.page;
		if ($scope.active_page === undefined)
		{
			$scope.active_page = 'all';
		}

		$scope.groupActive = (group) =>
		{
			if ($scope.idol_navigation.group == group)
			{
				return 'active';
			}
		}

		$scope.idolActive = (idol) =>
		{
			if ($scope.idol_navigation.idol == idol)
			{
				return 'active border-color-highlight bg-color-highlight';
			}
		}

		$scope.pageActive = (page) =>
		{
			if ($scope.active_page == page)
			{
				return 'active';
			}
		}
		
		$scope.$on('keydown', (_, e) =>
		{
			if (e.repeat || e.shiftKey || e.ctrlKey || e.altKey || e.metaKey) return;
			
			let number = parseInt(e.key);
			if (number !== undefined)
			{
				if (number == 0) number = 10;
				let index = number - 1;
				
				let keys = Object.keys(history_subpages);
				if (index < keys.length)
				{
					e.preventDefault();
					$route.updateParams({'page': keys[index]});
					return;
				}
			}
		});
		
		$scope.scrollPageSelectors = () =>
		{
			const scrollers = document.querySelectorAll('.page-selector');
			for (let scroller of scrollers)
			{
				const active = scroller.querySelector('a.active');
				if (!scroller || !active) continue;
				
				scroller.scrollLeft = 0;
				
				const scroller_rect = scroller.getBoundingClientRect();
				const scroller_width = scroller_rect.right - scroller_rect.left;
				
				const element = active.closest('li');
				
				const active_rect = element.getBoundingClientRect();
				const active_width = active_rect.right - active_rect.left;
				
				scroller.scrollLeft = active_rect.left - (scroller_width - active_width) / 2 - scroller_rect.left;
			}
		}
		
		setTimeout($scope.scrollPageSelectors);

		$scope.loading = false;
	}
)
