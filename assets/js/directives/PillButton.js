
app.directive('pillButton', function($parse, $timeout)
{
	return {
		restrict: 'A',
		transclude: true,
		scope: true,
		template: '<div class="inner"><div class="inner-dot">&nbsp;</div></div><div class="label">[[ label ]] <span class="hide-mobile" ng-if="keybind">([[ keybind ]])</span></div>',
		controller: function($scope, $transclude)
		{
			$transclude(function(clone, scope)
			{
				$scope.label = angular.element('<div>').append(clone).html().trim();
			});
		},
		link: function (scope, element, attrs)
		{
			let e = angular.element(element[0]); //.querySelector('div.pill-button');
			
			e.addClass('pill-button');
			
			scope.keybind = attrs.keybind;
			
			element.on('mousedown', function(event)
			{
				event.preventDefault();
				$parse(attrs.model).assign(scope.$parent, !$parse(attrs.model)(scope.$parent));
				scope.$parent.$apply();
			});

			scope.$parent.$watch(attrs.model, function(value)
			{
				if (value)
				{
					e.addClass('active').addClass('changed');
				}
				else
				{
					e.removeClass('active');
				}
				
				e.addClass('changed');
				$timeout(() => {
					e.removeClass('changed');
				}, 200);
			});
		}
	}
})

