
app.provider('SiteRoutes', function SiteRoutesProvider($routeProvider, $routeParamsProvider)
{
	class Route
	{
		id;
		title;
		path;
		controller;
		template;
		allowed_keys;
		error_redirect;
		subpages;
		subtitle;
		
		$angular = {};
			
		constructor(route_object)
		{
			const reserved_keys   = ['id', '$angular'];
			const assignable_keys = Reflect.ownKeys(this).filter(key => !reserved_keys.includes(key));
			
			for (const key of Reflect.ownKeys(route_object))
			{
				if (!assignable_keys.includes(key))
					throw Error("Unexpected key in route object: " + key)
				
				this[key] = route_object[key];
			}
			
			this.id = Route.make_path_id(this.path);
		}
		
		static make_path_id(path)
		{
			const path_base = path.substr(1).split('/')[0];
			if (path_base === '') return '__root__';
			return path_base;
		}
		
		get_subtitle()
		{
			if (this.subpages === undefined && this.subtitle === undefined)
				return undefined;
			
			const route_params = this.$angular.$route.current?.params || {};
			
			if (typeof this.subtitle == "function")
			{
				return this.subtitle.call(this, route_params);
			}
			
			if (this.subpages !== undefined && typeof this.subpages == "object" &&
				this.subtitle instanceof Array && this.subtitle.length == 2)
			{
				const property_key = this.subtitle[0];
				const default_key  = this.subtitle[1];
				
				let subpage_key = route_params[property_key];
				if (subpage_key === undefined)
				{
					subpage_key = default_key;
				}
				
				return this.subpages[subpage_key];
			}
			
			console.error("Route subtitle could not be determined. Check route subpages and subtitle.");			
			throw Error('Route.subtitle should be an array or a function.\n\nArray:\n  subtitle[0] : the route param property key searched for in subpages.\n  subtitle[1] : a default key to use if param property key is undefined.\n\nFunction:\n  First argument is current routeParams.\n  Should return the new subtitle or undefined if not set.');
			
			// return undefined;
		}
	}
	
	// -------------------------------------------
	
	this.registered_routes = {};
	
	var push_route = (route_config) =>
	{
		let route = new Route(route_config);
		if (route.id in this.registered_routes)
		{
			console.error("%c Route with same path has already been registered: " + route.id, "color:#f00; font-size:150%");
			return;
		}
		this.registered_routes[route.id] = route;
	}
	
	this.register_route = (new_routes) =>
	{
		push_route(new_routes);
		return this;
	}
	
	this.routes = () =>
	{
		return Object.values(this.registered_routes);
	}
	
	var $this = this;
	this.$get = function($rootScope, $location, $route)
	{
		for (let [route_id, route] of Object.entries($this.registered_routes))
		{
			route.$angular = {
				$location    : $location,
				$route       : $route,
			};
		}
		
		$this.get_active_route = () =>
		{
			const current_path = Route.make_path_id($location.path());
			if (current_path in $this.registered_routes)
				return $this.registered_routes[current_path];
			
			console.error("Route not found:", current_path, $this.registered_routes);
			return undefined;
		}
		
		$this.active_route = $this.get_active_route();
		
		$rootScope.$on('$locationChangeSuccess', (event) =>
		{
			$this.active_route = $this.get_active_route();
		});
		
		return {
			get : (route_id) =>
			{
				return $this.registered_routes[route_id];
			},
			
			routes : () =>
			{
				return $this.routes();
			},
			
			active_route : () =>
			{
				return $this.active_route;
			},
		};
	};
});
