
app.directive('countdown', function($rootScope, $parse, $window, $interval, RouteEvent)
{
	return {
		restrict: 'A',
		scope: true,
		link: function (scope, element, attrs)
		{
			scope.target_element = element[0];
			if (attrs.selector)
			{
				 const child_element = element[0].querySelector(attrs.selector);
				 console.log(element[0],  attrs.selector, child_element);
				 
				 if (child_element !== null)
				 {
					 scope.target_element = child_element; 	
				 }
			}
			
			scope.target = new Date(attrs.countdown * 1000);
			
			scope.update_time = () =>
			{
				const seconds = attrs.countdown - (Date.now() / 1000);
				
				if (seconds > 0)
				{
					scope.time_remaining = Utility.format_seconds_significant(seconds, 2);
					scope.target_element.innerHTML = scope.time_remaining;
				}
				else
				{
					scope.time_remaining = "&mdash;";
					
					if (attrs.finished)
					{
						element[0].innerHTML = attrs.finished.trim();
					}
					else
					{
						scope.target_element.innerHTML = scope.time_remaining;
					}
				}
				
				return seconds > 0;
			}
			
			scope.update_interval = $interval(() =>
			{
				if (!scope.update_time())
				{
					$interval.cancel(scope.update_interval);
				}
			}, 500);
			
			scope.update_time();
		}
	}
});
