
app.directive('scroll', function($parse, $window)
{
	return {
		link: function (scope, element, attrs)
		{
			let get_current_scroll = () =>
			{
				let doc = document.documentElement;
				return (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
			}
			let lastScroll = get_current_scroll();
			angular.element($window).on('scroll', function (e)
			{
				const current = get_current_scroll();
				const diff = current - lastScroll;
				lastScroll = current;
				scope.$apply(function()
				{
					scope.$eval(attrs.scroll, {$event: e, diff: diff});
				});
			});
		}
	}
});
