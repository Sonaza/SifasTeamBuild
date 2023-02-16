
app.factory('LocationKeys', ($rootScope, $location, SiteRoutes) =>
{
	class LocationKeysService
	{
		stored_keys = {}
		#internal = {};
		
		constructor()
		{
			this.stored_keys = $location.search();
			
			var that = this;
			$rootScope.$on("$locationChangeStart", function(event, next, current)
			{ 
				setTimeout(() => {that.update_keys()});
			});
		}
		
		update_keys()
		{
			const active_route = SiteRoutes.active_route();
			let allowed_keys = active_route.allowed_keys || [];
			
			let current_keys = Object.assign({}, $location.search());
			if (allowed_keys.length > 0)
			{
				for (const key of allowed_keys)
				{
					if (this.stored_keys[key] !== undefined && current_keys[key] === undefined)
					{
						current_keys[key] = this.stored_keys[key];
					}
				}
			}
			
			for (const key in current_keys)
			{
				if (!allowed_keys.includes(key))
				{
					delete current_keys[key];
				}
			}
			
			for (const key of allowed_keys)
			{
				if (key in current_keys && current_keys[key] !== undefined)
				{
					this.stored_keys[key] = current_keys[key];
				}
				else if (key in this.stored_keys)
				{
					delete this.stored_keys[key];
				}
			}
			
			if (!angular.equals(current_keys, $location.search()))
			{
				$location.search(current_keys).replace();
			}
		}
		
		get(key)
		{
			const current = this.stored_keys;
			if (key == undefined)
				return current;
			return current[key];
		}
		
		set(key, value)
		{
			$location.search(key, value).replace();
		}
		
		reset(key)
		{
			if (key in this.stored_keys)
			{
				delete this.stored_keys[key];
			}
			$location.search(key, undefined).replace();
		}
		
	};
	
	return new LocationKeysService();
});
