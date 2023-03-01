
let deferred_unloads_halted = false;

app.directive('deferredLoad', function($rootScope, $parse, $window, $timeout, RouteEvent)
{
	return {
		restrict: 'A',
		scope: true,
		// template: '<span class="deferred-loading" ng-if="!loaded">Loading...</span><ng-include onload="finished_loading()" class="deferred-load" src="get_template_url()">',
		template: '<span class="deferred-loading" ng-if="!loaded">Loading...</span><ng-include class="deferred-load" ng-if="loaded" src="template_url">',
		link: function (scope, element, attrs)
		{
			scope.last_checked = 0;
			scope.can_check = true;
			scope.refresh_loads = () =>
			{
				if (!scope.can_check || (Date.now() - scope.last_checked) < 40)
					return;
				
				scope.last_checked = Date.now();
				scope.can_check = false;
				
				// Needs slight delay just in case to let CSS changes propagate and stuff I guess
				$timeout(() =>
				{
					// scope.$apply(() =>
					// {
						scope.loaded = scope.should_be_visible();
						scope.can_check = true;
					// });
				});
			};
			
			scope.refresh_loads();
			
			$rootScope.$on("$viewContentLoaded", function(event, templateName)
			{
				scope.refresh_loads();
			});
			
			RouteEvent.element(window).on('scroll', () =>
			{
				scope.refresh_loads();
			});
			
			scope.$parent.$on('refresh-deferred-loads', () =>
			{
				scope.refresh_loads();
			});
			
			scope.loaded = false;
			scope.template_url = Utility.cache_buster('dist/pages/deferred/' + attrs.deferredLoad + '.html', BUILD_ID);
			
			// scope.finished_loading = () =>
			// {
			// 	if (scope.loaded)
			// 		scope.$parent.$broadcast('deferred-load-finished', attrs.deferredLoad, element[0]);
			// }
			
			scope.should_be_visible = function()
			{
				if (deferred_unloads_halted && scope.loaded)
					return true;
				
				return Utility.isElementPartiallyInViewport(element[0]);
			}
		}
	}
})

// function isElementInViewport(el)
// {
// 	let style = window.getComputedStyle(el);
// 	if (style.display === 'none')
// 		return false;
	
//     var rect = el.getBoundingClientRect();
//     return (
//         rect.top >= 0 &&
//         rect.left >= 0 &&
//         rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /* or $(window).height() */
//         rect.right <= (window.innerWidth || document.documentElement.clientWidth) /* or $(window).width() */
//     );
// }
