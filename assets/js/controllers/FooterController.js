
app.controller('FooterController', function($rootScope, $scope)
	{
		$scope.time_since = (iso_timestamp) =>
		{
			let time = new Date(iso_timestamp);
			if (!time) return "";
			let secondsDiff = (new Date().getTime() - time.getTime()) / 1000;
			return " (" + Utility.format_seconds(secondsDiff) + " ago)";
		}
	}
);
