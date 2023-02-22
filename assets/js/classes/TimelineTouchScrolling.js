
class TimelineTouchScrolling
{
	#$scope;
	#$window;
	
	active       = false;
	identifier   = undefined;
	
	
	initial      = {x: 0, y: 0};
	position     = {x: 0, y: 0};
	
	delta        = {x: 0, y: 0};
	velocity     = {x: 0, y: 0};
	axis         = false;
	
	last_move    = 0;
	
	has_momentum = false;
	
	timeline_element;
	// timeline_members_element;
	
	SiteSettings;
	
	constructor($scope, SiteSettings)
	{
		this.$scope = $scope;
		this.SiteSettings = SiteSettings;
		this.initialize($scope.RouteEvent);
	}
	
	is_active()
	{
		return this.active || this.has_momentum;
	}
	
	initialize(RouteEvent)
	{
		this.timeline_element = document.querySelector('#timeline');
		// this.timeline_members_element = document.querySelector('#timeline .timeline-members');
		
		RouteEvent.element(window).on('touchstart touchend', ($event) =>
		{
			if ($event.type == 'touchend')
			{
				if (this.active)
				{
					let identifier_found = false;
					for (const touch of $event.touches)
					{
						if (touch.identifier == this.identifier)
						{
							identifier_found = true;
							break;
						}
					}
					if (!identifier_found)
					{
						// console.log("STOPPING TOUCH SCROLL", $event);
						this.stop();
					}
				}
				return;
			}
			
			if ($event.type == 'touchstart')
			{
				if (!$event.target.closest('#timeline'))
					return;
				
				this.identifier = $event.changedTouches[0].identifier;
				this.position   = {
					x: $event.changedTouches[0].clientX,
					y: $event.changedTouches[0].clientY
				};
				
				this.initial = Utility.shallow_copy(this.position);
				
				this.start();
				
				$event.preventDefault();
			}
		});
		
		RouteEvent.element(window).on('touchmove', ($event) =>
		{
			let current_position = undefined;
			for (const touch of $event.touches)
			{
				if (touch.identifier == this.identifier)
				{
					current_position = {
						x: touch.clientX,
						y: touch.clientY,
					};
					break;
				}
			}
			if (current_position === undefined)
			{
				this.stop();
				return;
			}
			
			if (!this.active)
				return;
			
			const can_scroll = this.update(current_position);
			$event.preventDefault();
			// if (!can_scroll)
			// {
			// }
		},
		{
			capture: true,
			passive: false,
		});
	}
	
	start()
	{
		this.$scope.$apply(() =>
		{
			this.active = true;
			// this.SiteSettings.session_settings.disable_scrolling = false;
		});
	}
	
	stop()
	{
		if (!this.active)
			return;
		
		this.has_momentum = ((Date.now() - this.last_move) < 70) &&
			((Math.abs(this.delta.x) > 25) || (Math.abs(this.delta.y) > 25));
			
		this.$scope.$apply(() =>
		{
			this.active = false;
			// this.SiteSettings.session_settings.disable_scrolling = false;
		});
		
		if (this.has_momentum)
		{
			if (this.axis === false)
			{
				const delta_initial = {
					x: this.position.x - this.initial.x,
					y: this.position.y - this.initial.y
				};
				
				if (Math.abs(delta_initial.x) > Math.abs(delta_initial.y))
				{
					this.axis = 1;
				}
				else
				{
					this.axis = 2;
				}
			}
			
			this.velocity = Utility.shallow_copy(this.delta);
			this.update_momentum();
		}
		else
		{
			this.axis = false;
		}
	}
	
	update_mobile_cursor(delta)
	{
		if (this.axis == 2)
		{
			return true;
		}
		
		if (this.timeline_element.scrollLeft <= 0)
		{
			const cursor_rect = this.$scope.get_mobile_cursor_rect();
			const cursor_increment = -delta / cursor_rect.width;
		
			this.$scope.mobile_cursor += cursor_increment;
			this.$scope.mobile_cursor = Math.max(0, Math.min(0.5, this.$scope.mobile_cursor));
			this.$scope.update_mobile_indicator();
			
			const can_scroll = (this.$scope.mobile_cursor >= 0.5);
			return can_scroll;
		}
		
		const timeline_rect = this.timeline_element.getBoundingClientRect();
		const distance_left = this.timeline_element.scrollWidth - this.timeline_element.scrollLeft - timeline_rect.width;
		if (distance_left <= 0)
		{
			const cursor_rect = this.$scope.get_mobile_cursor_rect();
			const cursor_increment = -delta / cursor_rect.width;
			
			this.$scope.mobile_cursor += cursor_increment;
			this.$scope.mobile_cursor = Math.max(0.5, Math.min(1, this.$scope.mobile_cursor));
			this.$scope.update_mobile_indicator();
			return (this.$scope.mobile_cursor <= 0.5);
		}
		
		return true;
	}
	
	update(current_position)
	{
		if (!this.active)
			return;
		
		if (this.axis === false)
		{
			if (Utility.distance(current_position, this.initial) > 40)
			{
				const delta_initial = {
					x: current_position.x - this.initial.x,
					y: current_position.y - this.initial.y
				};
				
				if (Math.abs(delta_initial.x) > Math.abs(delta_initial.y))
				{
					this.axis = 1;
				}
				else
				{
					this.axis = 2;
				}
			}
		}
		
		this.delta = {
			x: current_position.x - this.position.x,
			y: current_position.y - this.position.y,
		};
		
		const can_scroll = this.update_mobile_cursor(this.delta.x);
		if (can_scroll)
		{
			if (this.axis == 1)
			{
				this.timeline_element.scrollLeft -= this.delta.x;
			}
			if (this.axis == 2)
			{
				document.documentElement.scrollTop -= this.delta.y;
			}
		}
		
		this.position = current_position;
		
		this.last_move = Date.now();
		
		return can_scroll;
	}
	
	update_momentum()
	{
		if (this.active)
		{
			this.has_momentum = false;
			this.axis = false;
			this.$scope.$apply();
			return;
		}
		
		this.velocity.x *= 0.92;
		this.velocity.y *= 0.92;
		
		// console.log("TOUCH MOMENTUM!", this.velocity);
		
		const can_scroll = this.update_mobile_cursor(this.velocity.x);
		if (can_scroll)
		{
			if (this.axis == 1)
			{
				this.timeline_element.scrollLeft -= this.velocity.x;
			}
			if (this.axis == 2)
			{
				document.documentElement.scrollTop -= this.velocity.y;
			}
		}
		
		const threshold = 0.2;
		if ((this.axis == 1 && Math.abs(this.velocity.x) < threshold) ||
			(this.axis == 2 && Math.abs(this.velocity.y) < threshold))
		{
			this.has_momentum = false;
			this.axis = false;
			this.$scope.$apply();
			return;
		}
		
		setTimeout(() => { this.update_momentum(); }, 7);
	}
	
};
