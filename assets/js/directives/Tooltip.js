
app.directive('tooltip', function($http, $compile, $templateCache)
{
	return {
		restrict: 'A',
		scope: true,
		link: function (scope, element, attrs)
		{
			scope.data = undefined;
			
			let template = $templateCache.get(attrs.tooltipTemplate);
			if (template !== undefined)
			{
				element.html(template);
				$compile(element.contents())(scope);
			}
			else
			{
				console.error("Tooltip template not preloaded:", attrs.tooltipTemplate);
				$http.get(attrs.tooltipTemplate)
					.then((response) =>
					{
						element.html(response.data);
						$compile(element.contents())(scope);
					});
			}
			
			scope.$parent.$watch(attrs.tooltip, function(tooltip_data)
			{
				if (tooltip_data)
				{
					scope.data = tooltip_data;
				}
			}, true);
		}
	}
})
