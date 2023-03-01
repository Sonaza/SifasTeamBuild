
app.provider('SiteRoutes', function SiteRoutesProvider($routeProvider, $routeParamsProvider)
{
	var $that = this;
	
	this.$location;
	this.$route;
	
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
		route_settings;
			
		constructor(route_object)
		{
			const reserved_keys   = ['id'];
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
		
		path_matches_current(page_path)
		{
			if (typeof page_path != "string" || page_path.length == 0)
			{
				throw new Error("Path must be a non-empty string.");
			}
			
			const path_tokens = page_path.substr(1).split('/');
			
			if (this.id === '__root__' && path_tokens[0] !== '')
			{
				return false;
			}
			if (this.id !== '__root__' && this.id !== path_tokens[0])
			{
				return false;
			}
			
			if (path_tokens.length > 1 && typeof this.subpages == "object")
			{
				if(!(path_tokens[1] in this.subpages))
				{
					return false;
				}
				
				const current_path = $that.$location.path().substr(1).split('/');
				if (current_path.length < 2)
				{
					return false;
				}
				
				if (current_path[1] !== path_tokens[1])
				{
					return false;
				}
			}
			
			return true;
		}
		
		get_subtitle()
		{
			if (this.subpages === undefined && this.subtitle === undefined)
				return undefined;
			
			// const route_params = this.$angular.$route.current?.params || {};
			const route_params = $that.$route.current?.params || {};
			
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
	
	this.configure = () =>
	{
		for (const route of this.routes())
		{
			$routeProvider.when(route.path, {
				controller:  route.controller,
				templateUrl: function(routeParams)
				{
					if (typeof route.template == "function")
					{
						let page_path = route.template(routeParams);
						if (page_path !== false)
						{
							return Utility.cache_buster('dist/pages/' + page_path, BUILD_ID);
						}
						else
						{
							return false;
						}
					}
					
					return Utility.cache_buster('dist/pages/' + route.template, BUILD_ID);
				},
				reloadOnSearch: route.reload || false,
				redirectTo : function(routeParams, locationPath, locationParams)
				{
					if (typeof route.template == "function")
					{
						let page_path = route.template(routeParams);
						if (page_path === false)
						{
							return route.error_redirect;
						}
					}
				},
			})
		}
		$routeProvider.otherwise({
			redirectTo: '/',
		});
	}
	
	this.$get = function($rootScope, $location, $route, SiteSettings)
	{
		$that.$location = $location;
		$that.$route = $route;
		
		$that.get_active_route = () =>
		{
			const current_path = Route.make_path_id($location.path());
			if (current_path in $that.registered_routes)
				return $that.registered_routes[current_path];
			
			console.error("Route not found:", current_path, $that.registered_routes);
			return undefined;
		}
		
		$that.active_route = $that.get_active_route();
		
		$rootScope.$on('$routeChangeSuccess', (event) =>
		{
			$that.active_route = $that.get_active_route();
			SiteSettings.route_settings = Utility.shallow_copy($that.active_route.route_settings || {});
		});
		
		return {
			get : (route_id) =>
			{
				return $that.registered_routes[route_id];
			},
			
			routes : () =>
			{
				return $that.routes();
			},
			
			active_route : () =>
			{
				return $that.active_route;
			},
		};
	};
});
