
app.directive('scrollbar', function($parse, $window, RouteEvent)
{
	return {
		restrict: 'A',
		scope: true,
		template: '<div class="scrollbar-groove"><div class="scrollbar-slider"></div></div>',
		link: function (scope, element, attrs)
		{
			let scrollbar = element[0];
			element.addClass('scrollbar');
			
			scope.scroll_progress = 0;
			scope.dragging = false;
			scope.can_set_scroll_position = false;
			
			let target_element  = document.querySelector(attrs.scrollbar);
			let scrollbar_groove = scrollbar.querySelector('.scrollbar-groove');
			let scrollbar_slider  = scrollbar.querySelector('.scrollbar-slider');
			
			scope.get_scrollable_width = () =>
			{
				const groove_rect = scrollbar_groove.getBoundingClientRect();
				const target_element_rect = target_element.getBoundingClientRect();
				return target_element.scrollWidth - target_element_rect.width;
			}
			
			scope.update_scroll_progress = () =>
			{
				scope.$apply(() => 
				{
					scope.scroll_progress = Math.min(1, target_element.scrollLeft / scope.get_scrollable_width());
				});
			}
			scope.update_slider_position = (scroll_progress) =>
			{
				const groove_rect = scrollbar_groove.getBoundingClientRect();
				const slider_rect = scrollbar_slider.getBoundingClientRect();
				scrollbar_slider.style.left = ((groove_rect.width - slider_rect.width) * scroll_progress) + 'px';
			}
			
			new ResizeObserver(() =>
			{
				scope.update_slider_position(scope.scroll_progress);
			}).observe(scrollbar)
			
			RouteEvent.element(target_element).on('scroll', () =>
			{
				scope.update_scroll_progress();
			});
			
			scope.$watch('scroll_progress', (scroll_progress) =>
			{
				scope.update_slider_position(scroll_progress);
				if (scope.can_set_scroll_position)
				{
					target_element.scrollLeft = scroll_progress * scope.get_scrollable_width();	
				}
				scope.can_set_scroll_position = false;
			});
			
			// ----------------------------------------------------------------------------
			// Generic Variables
			
			scope.jumping = {
				active      : false,
				last_jumped : 0,
			}
			
			// ----------------------------------------------------------------------------
			// Mouse Controls
			
			scope.grip_offset = 0;
			
			RouteEvent.element(window).on('mousedown mouseup', ($event) =>
			{
				if (Utility.mobile_mode())
					return;
				
				if ($event.type == 'mouseup')
				{
					if (scope.dragging)
					{
						scope.dragging = false;
						element.removeClass('dragging');
					}
					scope.jumping.active = false;
					return;
				}
				
				if ($event.button != 0 && $event.button != 2) // Left or right mouse
					return;
				
				if ($event.target == undefined || $event.target == null || $event.type != 'mousedown')
					return;
				
				let target_slider = $event.target.closest('.scrollbar-slider');
				if ($event.button == 0 && target_slider && target_slider == scrollbar_slider)
				{
					scope.dragging = true;
					element.addClass('dragging');
					
					let slider_rect = target_slider.getBoundingClientRect();
					scope.grip_offset = $event.pageX - slider_rect.left;
					
					$event.preventDefault();
					return;
				}
				
				let target_groove = $event.target.closest('.scrollbar-groove');
				if (target_groove && target_groove == scrollbar_groove)
				{
					const groove_rect = scrollbar_groove.getBoundingClientRect();
					const slider_rect = scrollbar_slider.getBoundingClientRect();
					
					const slider_position = Math.max(0, Math.min(groove_rect.width - slider_rect.width, $event.pageX - groove_rect.left - slider_rect.width / 2));
					const scrollable_groove_width = groove_rect.width - slider_rect.width;
					
					scope.$apply(() =>
					{
						scope.can_set_scroll_position = true;
						let new_progress = slider_position / scrollable_groove_width;
						
						if ($event.button == 0)
						{
							scope.jumping.active = true;
							scope.jumping.last_jumped = Date.now();
							
							let delta = (new_progress - scope.scroll_progress);
							if (Math.abs(delta) / 2.2 < 0.07)
							{
								scope.scroll_progress = new_progress;
							}
							else
							{
								scope.scroll_progress += delta / 2.2;
							}
						}
						else if ($event.button == 2)
						{
							scope.scroll_progress = new_progress;
						}
					});
					$event.preventDefault();
					return;
				}
			});
			
			RouteEvent.element(window).on('mousemove', ($event) =>
			{
				if (Utility.mobile_mode())
					return;
				
				if (!scope.dragging && !scope.jumping.active)
					return;
				
				const groove_rect = scrollbar_groove.getBoundingClientRect();
				const slider_rect = scrollbar_slider.getBoundingClientRect();
				
				const slider_position = Math.max(0, Math.min(groove_rect.width - slider_rect.width, $event.pageX - groove_rect.left - scope.grip_offset));
				const scrollable_groove_width = groove_rect.width - slider_rect.width;
				
				if (scope.dragging)
				{
					scope.$apply(() => 
					{
						scope.can_set_scroll_position = true;
						scope.scroll_progress = slider_position / scrollable_groove_width;
					});
				}
				else if (scope.jumping.active)
				{
					if ((Date.now() - scope.jumping.last_jumped) > 125)
					{
						scope.$apply(() =>
						{
							scope.can_set_scroll_position = true;
							let new_progress = slider_position / scrollable_groove_width;
							let delta = (new_progress - scope.scroll_progress);
							if (Math.abs(delta) / 3 < 0.04)
							{
								scope.scroll_progress = new_progress;
								scope.jumping.active = false;
							}
							else
							{
								scope.scroll_progress += delta / 3;
							}
						});
						scope.jumping.last_jumped = Date.now();
					}
				}
				$event.preventDefault();
			});
			
			RouteEvent.element(window).on('contextmenu', ($event) =>
			{
				if ($event.target.closest('.scrollbar') || (!$event.target.closest('.thumbnail') && $event.target.closest('#timeline')))
				{
					$event.preventDefault();
				}
			});
			
			// ----------------------------------------------------------------------------
			// Touch Controls
			
			scope.touch_dragging = {
				active      : false,
				identifier  : undefined,
				position    : {x: 0, y: 0},
				
				jumping     : false,
				last_jumped : 0,
			}
			
			RouteEvent.element(window).on('touchstart touchend', ($event) =>
			{
				if (scope.touch_dragging.active)
				{
					if ($event.type == 'touchend')
					{
						let identifier_found = false;
						for (const touch of $event.touches)
						{
							if (touch.identifier == scope.touch_dragging.identifier)
							{
								identifier_found = true;
								break;
							}
						}
						if (!identifier_found)
						{
							scope.touch_dragging.active = false;
							element.removeClass('dragging');
						}
					}
					return;
				}
				
				if ($event.type == 'touchstart')
				{
					let target_slider = $event.target.closest('.scrollbar-slider');
					if (target_slider && target_slider == scrollbar_slider)
					{
						scope.touch_dragging.active = true;
						scope.touch_dragging.identifier = $event.changedTouches[0].identifier;
						scope.touch_dragging.position   = {
							x: $event.changedTouches[0].clientX,
							y: $event.changedTouches[0].clientY
						};
						element.addClass('dragging');
						$event.preventDefault();
						return;
					}
					
					let target_groove = $event.target.closest('.scrollbar-groove');
					if (target_groove && target_groove == scrollbar_groove)
					{
						const groove_rect = scrollbar_groove.getBoundingClientRect();
						const slider_rect = scrollbar_slider.getBoundingClientRect();
						
						scope.touch_dragging.identifier = $event.changedTouches[0].identifier;
						scope.touch_dragging.position   = {
							x: $event.changedTouches[0].clientX,
							y: $event.changedTouches[0].clientY
						};
						
						const slider_position = Math.max(0, Math.min(groove_rect.width - slider_rect.width, scope.touch_dragging.position.x - groove_rect.left - slider_rect.width / 2));
						const scrollable_groove_width = groove_rect.width - slider_rect.width;
						
						scope.jumping.active = true;
						scope.jumping.last_jumped = Date.now();
						
						scope.$apply(() =>
						{
							scope.can_set_scroll_position = true;
							let new_progress = slider_position / scrollable_groove_width;
							let delta = (new_progress - scope.scroll_progress);
							if (Math.abs(delta) / 2.2 < 0.07)
							{
								scope.scroll_progress = new_progress;
							}
							else
							{
								scope.scroll_progress += delta / 2.2;
							}
						});
						$event.preventDefault();
					}
				}
			});
			
			RouteEvent.element(window).on('touchmove', ($event) =>
			{
				if (!scope.touch_dragging.active && !scope.jumping.active)
					return;
				
				let current_position = undefined;
				for (const touch of $event.touches)
				{
					if (touch.identifier == scope.touch_dragging.identifier)
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
					scope.touch_dragging.active = false;
					scope.jumping.active = false;
					element.removeClass('dragging');
					return;
				}
				
				const groove_rect = scrollbar_groove.getBoundingClientRect();
				const slider_rect = scrollbar_slider.getBoundingClientRect();
				
				const slider_position = Math.max(0, Math.min(groove_rect.width - slider_rect.width, current_position.x - groove_rect.left - slider_rect.width / 2));
				const scrollable_groove_width = groove_rect.width - slider_rect.width;
				
				if (scope.touch_dragging.active)
				{
					scope.$apply(() => 
					{
						scope.can_set_scroll_position = true;
						scope.scroll_progress = slider_position / scrollable_groove_width;
					});
					
					$event.preventDefault();
				}
				else if (scope.jumping.active)
				{
					const target_groove = $event.target.closest('.scrollbar-groove');
					if (target_groove != scrollbar_groove)
					{
						scope.jumping.active = false;
						return;
					}
					
					if ((Date.now() - scope.jumping.last_jumped) > 125)
					{
						scope.$apply(() =>
						{
							scope.can_set_scroll_position = true;
							let new_progress = slider_position / scrollable_groove_width;
							let delta = (new_progress - scope.scroll_progress);
							if (Math.abs(delta) / 3 < 0.04)
							{
								scope.scroll_progress = new_progress;
								scope.jumping.active = false;
							}
							else
							{
								scope.scroll_progress += delta / 3;
							}
						});
						scope.jumping.last_jumped = Date.now();
					}
					
					$event.preventDefault();
				}
				
				scope.touch_dragging.position = current_position;
			},
			{
				passive: false,
			});
		}
	}
});
