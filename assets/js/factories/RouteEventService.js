
app.factory('RouteEvent', ($rootScope, $route) =>
{
	class RouteEventService
	{
		current_route = undefined;
		event_listeners = []
				
		constructor()
		{
			var that = this;
			$rootScope.$on("$routeChangeStart", function($event, next_route, current_route)
			{
				for (let listener of that.event_listeners)
				{
					if (listener === false)
						continue;
					
					listener.abort_controller.abort();
				}
				that.event_listeners.length = 0;
				
				that.current_route = next_route;
			});
		}
		
		element(element)
		{
			if (typeof element == "string")
			{
				element = document.querySelector(element);
			}
			
			if (element?.addEventListener === undefined)
			{
				throw Error("Parameter element must be valid target for event listeners.");
			}
			
			let that = this;
			return {
				on : (event_names, listener, options = undefined) =>
				{
					that.listen(element, event_names, listener, options);
				}
			}
		}
		
		listen(element, event_names, listener, options = undefined)
		{
			if (element?.addEventListener === undefined)
			{
				throw Error("Parameter element must be valid target for event listeners.");
			}
			if (typeof event_names != "string" || event_names.length == 0)
			{
				throw Error("Parameter event_names must list listened events separated by a space.");
			}
			if (typeof listener != 'function')
			{
				throw Error("Parameter listener must be a function.");
			}
			
			let abort_controller = new AbortController();
			
			let listener_options = {
				once    : undefined,
				passive : undefined,
				capture : undefined,
				signal  : abort_controller.signal,
			}
			
			if (options instanceof Boolean)
			{
				listener_options.capture = options;
			}
			else if (typeof options == "object")
			{
				Object.assign(listener_options, options);
			}
			
			event_names = event_names.split(' ');
			
			let current_listener = {
				events   : event_names,
				listener : listener,
				options  : listener_options,
				abort_controller : abort_controller,
			}
			
			for (const event_name of event_names)
			{
				element.addEventListener(event_name, listener, listener_options);
			}
			
			this.event_listeners.push(current_listener);
			return current_listener;
		}
		
		off(listener)
		{
			const index = this.event_listeners.indexOf(listener);
			listener.signal.abort();
			
			this.event_listeners[index] = false;
		}
	};
	
	return new RouteEventService();
});
