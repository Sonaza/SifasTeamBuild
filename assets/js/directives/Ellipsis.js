
app.directive('ellipsis', function($window)
{
	return {
		restrict: 'A',
		link: function (scope, elements, attrs)
		{
			let element = elements[0];
			if (!element) return;
			
			let parent_selector = attrs['ellipsis'];
			if (!parent_selector) return;
			
			let parent = element.closest(parent_selector);
			if (!parent) return;
			
			let update = (event) =>
			{
				if (element.offsetWidth < element.scrollWidth)
				{
					angular.element(parent).addClass('text-overflowed');
				}
				else
				{
					angular.element(parent).removeClass('text-overflowed');
				}
			}
			update();
			
			angular.element($window).on('resize scroll', update);
		}
	}
})
