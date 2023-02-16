
app.directive('leftRightFlipper', function($parse, $timeout)
{
	return {
		restrict: 'A',
		scope: true,
		link: function (scope, element, attrs)
		{
			let e = element[0];
			scope.$parent.$watch(attrs.condition, function(condition)
			{
				if (condition)
				{
					e.style.left = 'auto';
					e.style.right = attrs.leftRightFlipper;
				}
				else
				{
					e.style.left = attrs.leftRightFlipper;
					e.style.right = 'auto';
				}
			});
		}
	}
})

