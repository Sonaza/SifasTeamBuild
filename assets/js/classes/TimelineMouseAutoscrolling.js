
class TimelineMouseAutoscrolling
{
	#$scope;
	#$window;
	
	active   = false;
	origin   = undefined;
	
	disabled = false;
	
	constructor($scope)
	{
		this.$scope = $scope;
		this.initialize($scope.RouteEvent);
	}
	
	is_active()
	{
		return this.active;
	}
	
	is_disabled()
	{
		return this.disabled;
	}
	
	set_disabled(disabled)
	{
		this.disabled = disabled;
	}
	
	initialize(RouteEvent)
	{
		RouteEvent.element(window).on('mousedown mouseup', ($event) =>
		{
			if ($event.button != 1) // Middle mouse
				return;
			
			if (this.active && $event.target.closest('.thumbnail'))
			{
				$event.preventDefault();
				return;
			}
			
			// Only stop on mouseup if cursor has moved
			if (this.active && $event.type == 'mouseup')
			{
				this.stop(14);
				return;
			}
			
			if (this.$scope.mouse_dragging.is_active())
				return;
			
			// Autoscrolling is temporarily disabled
			if (this.disabled)
				return;
			
			if (!$event.target.closest('#timeline') || $event.type != 'mousedown')
				return;
			
			if (!this.active)
			{
				this.start();
			}
			else
			{
				this.stop();
			}
			
			$event.preventDefault();
		});
	}
	
	start()
	{
		if (Utility.mobile_mode())
			return;
			
		this.origin = {
			x: this.$scope.mouse.absolute.x,
			y: this.$scope.mouse.absolute.y,
		}
		
		this.active = true;
		
		const origin_element = document.querySelector('#timeline-autoscroll-origin');
		if (origin_element)
		{
			origin_element.style.left = (this.origin.x) + 'px';
			origin_element.style.top =  (this.origin.y) + 'px';
			origin_element.style.display = 'block';
		}
		this.$scope.$apply();
		
		this.update();
	}
	
	stop(minimum_delta = 0)
	{
		if (!Utility.mobile_mode())
		{
			if (minimum_delta > 0)
			{
				const delta = {
					x: this.$scope.mouse.absolute.x - this.origin.x,
					y: this.$scope.mouse.absolute.y - this.origin.y,
				}
				if (Math.abs(delta.x) < minimum_delta && Math.abs(delta.y) < minimum_delta)
				{
					return;
				}
			}
		}
		
		this.active = false;
		
		const origin_element = document.querySelector('#timeline-autoscroll-origin');
		if (origin_element)
		{
			origin_element.style.display = 'none';
		}
	}
	
	update()
	{
		if (!this.active)
			return;
		
		if (Utility.mobile_mode())
		{
			this.stop();
			return;
		}
		
		const delta = {
			x: this.$scope.mouse.absolute.x - this.origin.x,
			y: this.$scope.mouse.absolute.y - this.origin.y,
		}
		
		const deadzone = 25;
		if (Math.abs(delta.x) >= deadzone)
		{
			const timeline_element = document.querySelector('#timeline');
			timeline_element.scrollLeft += Math.min(400, Utility.abs_subtract(delta.x, deadzone)) / 2;
		}
		if (Math.abs(delta.y) >= deadzone)
		{
			document.documentElement.scrollTop += Math.min(200, Utility.abs_subtract(delta.y, deadzone) / 3) / 2;
		}
		setTimeout(() => { this.update(); }, 15);
	}
}
