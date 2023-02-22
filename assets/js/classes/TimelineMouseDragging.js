
class TimelineMouseDragging
{
	#$scope;
	#$window;
	
	active       = false;
	velocity     = {x: 0, y: 0};
	last_move    = 0;
	unhighlit    = false;
	has_momentum = false;
	
	constructor($scope)
	{
		this.$scope = $scope;
		this.initialize($scope.RouteEvent);
	}
	
	is_active()
	{
		return (this.active && this.unhighlit) || this.has_momentum;
	}
	
	initialize(RouteEvent)
	{
		RouteEvent.element(window).on('mousedown mouseup', ($event) =>
		{
			if ($event.button != 0 || Utility.mobile_mode()) // Left mouse
				return;
			
			if (this.active && $event.type == 'mouseup')
			{
				this.stop();
				return;
			}
			
			if (this.active)
				return;
			
			if (!$event.target.closest('#timeline') || $event.type != 'mousedown')
				return;
			
			if ($event.target.closest('.thumbnail') || $event.target.closest('.timeline-members'))
				return;
			
			this.start();
			$event.preventDefault();
		});
		
		RouteEvent.element(window).on('mousemove', ($event) =>
		{
			this.update();
		});
	}
	
	start()
	{
		if (Utility.mobile_mode())
			return;
		
		this.unhighlit = false;
		
		this.$scope.$apply(() =>
		{
			this.active = true;
		});
	}
	
	stop()
	{
		this.has_momentum = ((Date.now() - this.last_move) < 70) &&
			((Math.abs(this.velocity.x) > 1) || (Math.abs(this.velocity.y) > 1));
		
		this.$scope.$apply(() =>
		{
			this.active = false;
		});
				
		if (this.has_momentum)
		{
			this.update_momentum();
		}
		else
		{
			this.$scope.update_timeline_indicator();
		}
	}
	
	update()
	{
		if (!this.active)
			return;
		
		if (!this.unhighlit)
		{
			this.$scope.unhighlight_everything();
			this.unhighlit = true;
		}
		
		this.last_move = Date.now();
		
		this.velocity.x = this.$scope.mouse.movement.x;
		this.velocity.y = this.$scope.mouse.movement.y;
		
		const timeline_element = document.querySelector('#timeline');
		timeline_element.scrollLeft -= this.$scope.mouse.movement.x;
		document.documentElement.scrollTop -= this.$scope.mouse.movement.y;	
	}
	
	update_momentum()
	{
		if (this.active)
		{
			this.$scope.$apply(() =>
			{
				this.has_momentum = false;
			});
			return;
		}
		
		this.velocity.x *= 0.85;
		this.velocity.y *= 0.85;
		
		const timeline_element = document.querySelector('#timeline');
		timeline_element.scrollLeft -= this.velocity.x;
		document.documentElement.scrollTop -= this.velocity.y;
		
		const threshold = 0.2;
		if (Math.abs(this.velocity.x) < threshold || 
			Math.abs(this.velocity.y) < threshold)
		{
			this.has_momentum = false;
			return;
		}
		
		setTimeout(() => { this.update_momentum(); }, 15);
	}
	
}
