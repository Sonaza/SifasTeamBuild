
const month_names = [
	'January',
	'February',
	'March',
	'April',
	'May',
	'June',
	'July',
	'August',
	'September',
	'October',
	'November',
	'December',
];

app.config(function(SiteSettingsProvider, SiteRoutesProvider)
{
	SiteRoutesProvider.register_route(
	{
		title        : 'Timeline',
		path         : '/timeline/:locale?',
		controller   : 'TimelineController',
		template     : function(routeParams)
		{
			if (routeParams.locale !== undefined && (routeParams.locale == "jp" || routeParams.locale == "ww"))
			{
				return 'timeline_' + routeParams.locale + '.html';
			}
			
			return SiteSettingsProvider.settings.global_dates ? 'timeline_ww.html' : 'timeline_jp.html';
		},
		allowed_keys : ['timeline_position'],
	});
});

app.filter('reverse', function()
{
	return function(items, is_reversed)
	{
		return is_reversed ? items.slice().reverse() : items;
	};
});

const member_birthday_phrase = 
{
	8   :  "It's Hanayo's birthday!<br>Have a riceball?",               // Hanayo
	5   :  "It's Rin's birthday, nya!",                                 // Rin
	6   :  "Geez, I guess it's Maki's birthday!",                       // Maki
	
	1   :  "It's Honoka's birthday!<br>Faito da yo!",                   // Honoka
	3   :  "It's Kotori's birthday, chirp chirp!",                        // Kotori
	4   :  "It's Umi's birthday,<br>Love Arrow Shoot!",                 // Umi
	
	7   :  "The stars have aligned:<br>it's Nozomi's birthday!",        // Nozomi
	2   :  "It's Eli's birthday, harasho!",                             // Eli
	9   :  "It's Nico's birthday,<br>Nico-Nico-nii!",                   // Nico
	
	
	107 :  "It's Hanamaru's birthday, zura!",                           // Hanamaru
	106 :  "It's Yohane's birthday,<br>little demons!",                 // Yoshiko
	109 :  "It's Ruby's birthday, eek!",                                // Ruby
	
	101 :  "It's Chika's birthday,<br>let's shine together!",           // Chika
	102 :  "Play the piano for Riko's birthday!",                       // Riko
	105 :  "It's You's birthday, yousoro!",                             // You
	
	103 :  "It's Kanan's birthday, let's hug!",                         // Kanan
	104 :  "It's Dia's birthday, desu wa!",                             // Dia
	108 :  "It's Mari's birthday, shiny!",                              // Mari
	
	
	209 :  "Rina-chan board says:<br>It's my birthday!",                // Rina
	202 :  "It's Kasumi's birthday!<br>Tell me I'm cute?",              // Kasumi
	203 :  "All the world's a stage<br>for Shizuku's birthday!",        // Shizuku
	210 :  "Have you prepared a present?<br>It's Shioriko's birthday!", // Shioriko
	
	201 :  "It's Ayumu's birthday, ayu-pyon!",                          // Ayumu
	207 :  "Get fired up, it's Setsuna's birthday!",                    // Setsuna
	205 :  "It's Ai's birthdai, geddit?",                               // Ai
	212 :  "It's Lanzhu's birthday, praise me!",                        // Lanzhu
	
	208 :  "È il compleanno di Emma, evviva!",                          // Emma
	206 :  "It's Kanata's birthday... Zzz...",                          // Kanata
	204 :  "Keep your eyes on Karin,<br>it's her birthday!",            // Karin
	211 :  "Hey Baby-chan,<br>celebrate Mia's birthday!",               // Mia
}

app.controller('TimelineController', function($rootScope, $scope, $route, $routeParams, $location, $window, $timeout, SiteSettings, LocationKeys)
{
	const date_format = '{} {}';
	const hovered_day_format = 'day-hovered-{}';
	const hovered_item_class_format = '.tl-{}-id-{}';
	
	$scope.member_birthday_phrase = member_birthday_phrase;
	
	const CardDisplayMode =
	{
		SHOW_ALL     : 0,
		SHOW_UR_ONLY : 1,
		SHOW_SR_ONLY : 2,
	}
	
	$scope.current_month_label = "";
	
	$scope.loading = true;
	
	let params = LocationKeys.get();
	
	if ($routeParams.locale === undefined)
	{
		LocationKeys.reset('timeline_position');
		
		let current_locale = $rootScope.settings.global_dates ? "ww" : "jp";
		$location.path('/timeline/' + current_locale);
	}
	else if (params.timeline_position !== undefined)
	{
		let current_locale = $rootScope.settings.global_dates ? "ww" : "jp";
		if ($routeParams.locale != current_locale)
		{
			$rootScope.settings.global_dates = !$rootScope.settings.global_dates;
		}
	}
	
	$scope.$watch('$root.settings.global_dates', function()
	{
		let current_locale = $rootScope.settings.global_dates ? "ww" : "jp";
		if ($routeParams.locale != current_locale)
		{
			CardTooltip.toggleTooltip(undefined, undefined, false);
			if ($routeParams.locale !== undefined)
			{
				let position = $scope.get_timeline_position();
				LocationKeys.set('timeline_position', position.equivalent);
			}
			$location.path('/timeline/' + current_locale);
		}
	});
	
	$scope.timeline_settings = {
		target_month : params.timeline_position,
		display_mode : CardDisplayMode.SHOW_ALL,
	}
	
	$scope.highlight_stripes = () =>
	{
		if (!Utility.mobile_mode() && $scope.hovered_idol_id)
		{
			return 'highlight-stripe-' + $scope.hovered_idol_id;
		}
		return '';
	}
	
	$scope.timeline_classes = () =>
	{
		let output = [];
		if ($rootScope.settings.timeline_show_events)
		{
			output.push('show-events');
		}
		if ($rootScope.settings.timeline_show_banners)
		{
			output.push('show-banners');
		}
		if ($scope.timeline_settings.display_mode)
		{
			output.push('display-mode-' + $scope.timeline_settings.display_mode);
		}
		
		if ($scope.autoscroll.active)
		{
			output.push('autoscrolling');
		}
		
		if ($scope.grab_scroll.active)
		{
			output.push('dragging');
		}
		
		return output.join(' ');
	}
	
	// ---------------------------------------------------------
	
	const timeline_element = document.querySelector('#timeline');
	const timeline_members_element = document.querySelector('#timeline .timeline-members');
	
	$scope.timeline_data = JSON.parse(timeline_element.getAttribute('data-timeline-data'));
	for (let [event_id, event_data] of Object.entries($scope.timeline_data['events']))
	{
		event_data.type     = EventType.types_by_id[event_data.type];
		event_data.featured = Member.members_by_id[event_data.featured];
		event_data.gacha    = event_data.gacha.map((key) => Member.members_by_id[key]);
	}
	for (let [banner_id, banner_data] of Object.entries($scope.timeline_data['banners']))
	{
		banner_data.type     = BannerType.types_by_id[banner_data.type];
	}
	
	$scope.timeline_timespan = {
		years           : [],
		months_in_years : {},
	};
	for (let [year, month_data] of Object.entries($scope.timeline_data.months))
	{
		$scope.timeline_timespan.years.push(year);
		$scope.timeline_timespan.months_in_years[year] = [];
		for (let month = month_data[0]; month <= month_data[1]; month++)
		{
			$scope.timeline_timespan.months_in_years[year].push([month, month_names[month - 1]]);
		}
	}
	
	// ---------------------------------------------------------
	
	const indicator_line = document.querySelector('#timeline-indicator-line');
	console.assert(indicator_line, "indicator_line null");
	const date_highlight = document.querySelector('#timeline-date-highlight');
	console.assert(date_highlight, "date_highlight null");
	const date_tooltip   = document.querySelector('#timeline-date-tooltip');
	console.assert(date_tooltip, "date_tooltip null");
	
	// ----------------------------------------------------------------------------
	// Mouse Controls
	
	$scope.mouse = {
		absolute : {x: 0, y: 0},
		page     : {x: 0, y: 0},
		target   : undefined,
		movement : {x: 0, y: 0},
		relative : (element) =>
		{
			const rect = element.getBoundingClientRect();
			return {
				x: $scope.mouse.absolute.x - rect.x,
				y: $scope.mouse.absolute.y - rect.y,
			}
		}
	};
	
	angular.element($window).on('mousemove', ($event) =>
	{
		if (!Utility.mobile_mode())
		{
			$scope.mouse.absolute.x = $event.clientX;
			$scope.mouse.absolute.y = $event.clientY;
			$scope.mouse.page.x     = $event.pageX;
			$scope.mouse.page.y     = $event.pageY;
			$scope.mouse.target     = $event.target;
			$scope.mouse.movement.x = $event.movementX;
			$scope.mouse.movement.y = $event.movementY;
		}
		
		$scope.grab_scroll.update();
		$scope.update_timeline_indicator();
	});
	
	$scope.grab_scroll = {
		active       : false,
		velocity     : {x: 0, y: 0},
		last_move    : 0,
		unhighlit    : false,
		has_momentum : false,
		start : () =>
		{
			if (Utility.mobile_mode())
				return;
			
			$scope.grab_scroll.unhighlit = false;
			
			$scope.$apply(() =>
			{
				$scope.grab_scroll.active = true;
			});
		},
		stop : () =>
		{
			$scope.grab_scroll.has_momentum = ((Date.now() - $scope.grab_scroll.last_move) < 70) &&
				((Math.abs($scope.grab_scroll.velocity.x) > 1) || (Math.abs($scope.grab_scroll.velocity.y) > 1));
			
			$scope.$apply(() =>
			{
				$scope.grab_scroll.active = false;
				
				$timeout(() =>
				{
					if (!$scope.grab_scroll.has_momentum)
					{
						$scope.restore_highlights();
					}
				});
			});
			
			
			if ($scope.grab_scroll.has_momentum)
			{
				$scope.grab_scroll.update_momentum();
			}
		},
		update : () =>
		{
			if (!$scope.grab_scroll.active)
				return;
			
			if (!$scope.grab_scroll.unhighlit)
			{
				$scope.set_indicator_opacity(0);
				$scope.unhighlight_everything();
				$scope.grab_scroll.unhighlit = true;
			}
			
			$scope.grab_scroll.last_move = Date.now();
			
			$scope.grab_scroll.velocity.x = $scope.mouse.movement.x;
			$scope.grab_scroll.velocity.y = $scope.mouse.movement.y;
			
			timeline_element.scrollLeft -= $scope.mouse.movement.x;
			document.documentElement.scrollTop -= $scope.mouse.movement.y;	
		},
		update_momentum : () =>
		{
			if ($scope.grab_scroll.active)
			{
				$scope.restore_highlights();
				$scope.grab_scroll.has_momentum = false;
				return;
			}
			
			$scope.grab_scroll.velocity.x *= 0.85;
			$scope.grab_scroll.velocity.y *= 0.85;
			
			// console.log("GRAB MOMENTUM!", $scope.grab_scroll.velocity);
			
			timeline_element.scrollLeft -= $scope.grab_scroll.velocity.x;
			document.documentElement.scrollTop -= $scope.grab_scroll.velocity.y;
			
			const threshold = 0.2;
			if (Math.abs($scope.grab_scroll.velocity.x) < threshold || 
				Math.abs($scope.grab_scroll.velocity.y) < threshold)
			{
				$scope.restore_highlights();
				$scope.grab_scroll.has_momentum = false;
				return;
			}
			
			setTimeout(() => { $scope.grab_scroll.update_momentum(); }, 15);
		},
	};
	
	
	$scope.autoscroll = {
		active   : false,
		origin   : undefined,
		disable  : false,
		start    : () =>
		{
			if (Utility.mobile_mode())
				return;
				
			$scope.autoscroll.origin = {
				x: $scope.mouse.absolute.x,
				y: $scope.mouse.absolute.y,
			}
			$scope.autoscroll.active = true;
			
			const origin_element = document.querySelector('#timeline-autoscroll-origin');
			if (origin_element)
			{
				origin_element.style.left = ($scope.autoscroll.origin.x) + 'px';
				origin_element.style.top =  ($scope.autoscroll.origin.y) + 'px';
				origin_element.style.display = 'block';
			}
			
			$scope.autoscroll.update();
		},
		stop     : (minimum_delta = 0) =>
		{
			if (!Utility.mobile_mode())
			{
				if (minimum_delta > 0)
				{
					const delta = {
						x: $scope.mouse.absolute.x - $scope.autoscroll.origin.x,
						y: $scope.mouse.absolute.y - $scope.autoscroll.origin.y,
					}
					if (Math.abs(delta.x) < minimum_delta && Math.abs(delta.y) < minimum_delta)
					{
						return;
					}
				}
			}
			
			$scope.autoscroll.active = false;
			
			const origin_element = document.querySelector('#timeline-autoscroll-origin');
			if (origin_element)
			{
				origin_element.style.display = 'none';
			}
		},
		update  : () =>
		{
			if (!$scope.autoscroll.active)
				return;
			
			if (Utility.mobile_mode())
			{
				$scope.autoscroll.stop();
				return;
			}
			
			const delta = {
				x: $scope.mouse.absolute.x - $scope.autoscroll.origin.x,
				y: $scope.mouse.absolute.y - $scope.autoscroll.origin.y,
			}
			
			const deadzone = 25;
			if (Math.abs(delta.x) >= deadzone)
			{
				timeline_element.scrollLeft += Math.min(400, Utility.abs_subtract(delta.x, deadzone)) / 2;
			}
			if (Math.abs(delta.y) >= deadzone)
			{
				document.documentElement.scrollTop += Math.min(200, Utility.abs_subtract(delta.y, deadzone) / 3) / 2;
			}
			setTimeout(() => { $scope.autoscroll.update(); }, 15);
		},
	};
	
	angular.element($window).on('mousedown mouseup', ($event) =>
	{
		if ($event.button == 0 && !Utility.mobile_mode()) // Left mouse
		{
			if ($scope.grab_scroll.active && $event.type == 'mouseup')
			{
				$scope.grab_scroll.stop();
				return;
			}
			
			if ($scope.autoscroll.active)
				return;
			
			if (!$event.target.closest('#timeline') || $event.type != 'mousedown')
				return;
			
			if ($event.target.closest('.thumbnail') || $event.target.closest('.timeline-members'))
				return;
			
			$scope.grab_scroll.start();
			$event.preventDefault();
		}
		
		if ($event.button == 1) // Middle mouse
		{
			if ($scope.autoscroll.active && $event.target.closest('.thumbnail'))
			{
				$event.preventDefault();
				return;
			}
			
			// Only stop on mouseup if cursor has moved
			if ($scope.autoscroll.active && $event.type == 'mouseup')
			{
				$scope.autoscroll.stop(14);
				return;
			}
			
			if ($scope.grab_scroll.active)
				return;
			
			// Autoscrolling is temporarily disabled
			if ($scope.autoscroll.disable)
				return;
			
			if (!$event.target.closest('#timeline') || $event.type != 'mousedown')
				return;
			
			if (!$scope.autoscroll.active)
			{
				$scope.autoscroll.start();
			}
			else
			{
				$scope.autoscroll.stop();
			}
			
			$event.preventDefault();
		}
	});
	
	angular.element(timeline_element).on('mouseover mouseout', ($event) =>
	{
		let timeline_members = $event.target.closest('.timeline-members');
		if (timeline_members)
			return;
		
		if ($scope.grab_scroll.active || $scope.grab_scroll.has_momentum)
			return;
		
		if ($event.type == 'mouseover')
		{
			$scope.set_indicator_opacity(1);
		}
		else if ($event.type == 'mouseout')
		{
			$scope.set_indicator_opacity(0);
			$scope.unhighlight_everything();
		}
	});
	
	// ----------------------------------------------------------------------------
	
	$scope.current_mobile_mode = Utility.mobile_mode();
	
	angular.element($window).on('resize', ($event) =>
	{
		$scope.autoscroll.stop();
		$scope.set_indicator_opacity(0);
		$scope.unhighlight_everything();
		date_tooltip.style.left = undefined;
		date_tooltip.style.top = undefined;
		date_tooltip.style.bottom = undefined;
		date_tooltip.style.marginLeft = undefined;
		
		// $timeout(() => 
		// {
		// 	if ($scope.current_mobile_mode != Utility.mobile_mode())
		// 	{
		// 		location.reload();
		// 	}
		// }, 50);
	});
	
	$scope.$watch('$root.settings.order_reversed', function(new_reversed, old_reversed)
	{
		if (new_reversed == old_reversed)
			return;
		
		$scope.$broadcast('refresh-deferred-loads');
		
		const rect = timeline_element.getBoundingClientRect();
		const distance_left = timeline_element.scrollWidth - timeline_element.scrollLeft - rect.width;
		
		// Keep the current scroll position if near start or end
		if (timeline_element.scrollLeft < 100 || distance_left < 100)
		{
			$timeout(() =>
			{
				$scope.update_timeline_position_param();
			})
			return;
		}
			
		deferred_unloads_halted = true;
		$scope.position_update_halted = true;
		
		$timeout(() => {
			$scope.jump_to_position($scope.timeline_settings.target_month);
		}, 50);
		
		$timeout(() => {
			$scope.jump_to_position($scope.timeline_settings.target_month);
			deferred_unloads_halted = false;
			
			$timeout(() =>
			{
				$scope.position_update_halted = false;
				$scope.update_timeline_position_param();
			});
		}, 100);
	});
	
	// ----------------------------------------------------------------------------
	
	angular.element(timeline_element).on('scroll', ($event) =>
	{
		$scope.$broadcast('refresh-deferred-loads');
		if (Utility.mobile_mode())
		{
			const timeline_rect = timeline_element.getBoundingClientRect();
			const distance_left = timeline_element.scrollWidth - timeline_element.scrollLeft - timeline_rect.width;
			
			if (timeline_element.scrollLeft > 0 && distance_left > 0)
			{
				$scope.mobile_cursor = 0.5;
			}
			
			$scope.update_mobile_indicator();
		}
		else
		{
			$scope.update_timeline_indicator();
			$scope.update_timeline_position_param();
		}
	});
	
	$scope.get_mobile_cursor_rect = () =>
	{
		const timeline_rect = timeline_element.getBoundingClientRect();
		const timeline_members_rect = timeline_members_element.getBoundingClientRect();
		return {
			top    : timeline_rect.top,
			left   : timeline_rect.left + timeline_members_rect.width,
			width  : timeline_rect.width - timeline_members_rect.width,
			height : timeline_rect.height,
		}
	}
	
	$scope.update_mobile_indicator = () =>
	{
		const cursor_rect = $scope.get_mobile_cursor_rect();
		
		const doc = document.documentElement;
		$scope.mouse.absolute.x = cursor_rect.left + $scope.mobile_cursor * cursor_rect.width;
		$scope.mouse.absolute.y = doc.clientHeight / 2;
		$scope.mouse.absolute.y = cursor_rect.top + 50 + doc.scrollTop;
		
		$scope.mouse.page.x     = $scope.mouse.absolute.x + doc.scrollLeft;
		$scope.mouse.page.y     = doc.clientHeight / 2 + doc.scrollTop;
		$scope.mouse.target     = document.elementFromPoint($scope.mouse.absolute.x, $scope.mouse.absolute.y);
		$scope.mouse.movement.x = 0;
		$scope.mouse.movement.y = 0;
		
		// console.debug($scope.mouse.target.closest('.month')?.getAttribute('data-month-key'));
		
		// $scope.mouse.absolute.x = doc.clientWidth / 2 - 100 + $scope.mobile_cursor
		// $scope.mouse.page.x     = doc.clientWidth / 2 + doc.scrollLeft;
		
		$scope.update_timeline_indicator();
		$scope.update_timeline_position_param();
	}
	
	// ----------------------------------------------------------------------------
	// Touch Controls
	
	// $scope.$watch('mobile_cursor', function(new_value, old_value)
	// {
	// 	$timeout(() =>
	// 	{
	// 		$scope.update_mobile_indicator();
	// 	});
	// });
	
	$scope.touch_scrolling = {
		active       : false,
		identifier   : undefined,
		
		initial      : {x: 0, y: 0},
		position     : {x: 0, y: 0},
		
		delta        : {x: 0, y: 0},
		velocity     : {x: 0, y: 0},
		axis         : false,
		
		last_move    : 0,
		
		has_momentum : false,
		start : () =>
		{
			$scope.$apply(() =>
			{
				$scope.touch_scrolling.active = true;
				SiteSettings.session_settings.disable_scrolling = true;
			});
		},
		stop : () =>
		{
			if (!$scope.touch_scrolling.active)
				return;
			
			$scope.touch_scrolling.has_momentum = ((Date.now() - $scope.touch_scrolling.last_move) < 70) &&
				((Math.abs($scope.touch_scrolling.delta.x) > 1) || (Math.abs($scope.touch_scrolling.delta.y) > 1));
				
			console.log($scope.touch_scrolling.has_momentum, $scope.touch_scrolling.delta);
			
			$scope.$apply(() =>
			{
				$scope.touch_scrolling.active = false;
				SiteSettings.session_settings.disable_scrolling = false;
			});
			
			if ($scope.touch_scrolling.has_momentum)
			{
				if ($scope.touch_scrolling.axis === false)
				{
					const delta_initial = {
						x: $scope.touch_scrolling.position.x - $scope.touch_scrolling.initial.x,
						y: $scope.touch_scrolling.position.y - $scope.touch_scrolling.initial.y
					};
					
					if (Math.abs(delta_initial.x) > Math.abs(delta_initial.y))
					{
						$scope.touch_scrolling.axis = 1;
					}
					else
					{
						$scope.touch_scrolling.axis = 2;
					}
				}
				
				$scope.touch_scrolling.velocity = Utility.shallow_copy($scope.touch_scrolling.delta);
				$scope.touch_scrolling.update_momentum();
			}
			else
			{
				$scope.touch_scrolling.axis = false;
			}
		},
		update_mobile_cursor : (delta) =>
		{
			if ($scope.touch_scrolling.axis == 2)
			{
				return true;
			}
			
			if (timeline_element.scrollLeft <= 0)
			{
				const cursor_rect = $scope.get_mobile_cursor_rect();
				const cursor_increment = -delta / cursor_rect.width;
			
				$scope.mobile_cursor += cursor_increment;
				$scope.mobile_cursor = Math.max(0, Math.min(0.5, $scope.mobile_cursor));
				$scope.update_mobile_indicator();
				return ($scope.mobile_cursor >= 0.5);
			}
			
			const timeline_rect = timeline_element.getBoundingClientRect();
			const distance_left = timeline_element.scrollWidth - timeline_element.scrollLeft - timeline_rect.width;
			if (distance_left <= 0)
			{
				const cursor_rect = $scope.get_mobile_cursor_rect();
				const cursor_increment = -delta / cursor_rect.width;
				
				$scope.mobile_cursor += cursor_increment;
				$scope.mobile_cursor = Math.max(0.5, Math.min(1, $scope.mobile_cursor));
				$scope.update_mobile_indicator();
				return ($scope.mobile_cursor <= 0.5);
			}
			
			return true;
		},
		update : (current_position) =>
		{
			if (!$scope.touch_scrolling.active)
				return;
			
			$scope.touch_scrolling.delta = {
				x: current_position.x - $scope.touch_scrolling.position.x,
				y: current_position.y - $scope.touch_scrolling.position.y,
			};
			
			if ($scope.touch_scrolling.axis === false)
			{
				if (Utility.distance(current_position, $scope.touch_scrolling.initial) > 60)
				{
					const delta_initial = {
						x: current_position.x - $scope.touch_scrolling.initial.x,
						y: current_position.y - $scope.touch_scrolling.initial.y
					};
					
					if (Math.abs(delta_initial.x) > Math.abs(delta_initial.y))
					{
						$scope.touch_scrolling.axis = 1;
					}
					else
					{
						$scope.touch_scrolling.axis = 2;
					}
				}
			}
			
			const can_scroll = $scope.touch_scrolling.update_mobile_cursor($scope.touch_scrolling.delta.x);
			if (can_scroll)
			{
				if ($scope.touch_scrolling.axis == 1)
				{
					timeline_element.scrollLeft -= $scope.touch_scrolling.delta.x;
				}
				if ($scope.touch_scrolling.axis == 2)
				{
					document.documentElement.scrollTop -= $scope.touch_scrolling.delta.y;
				}
			}
			
			$scope.touch_scrolling.position = current_position;
			
			$scope.touch_scrolling.last_move = Date.now();
		},
		update_momentum : () =>
		{
			if ($scope.touch_scrolling.active)
			{
				$scope.touch_scrolling.has_momentum = false;
				$scope.touch_scrolling.axis = false;
				return;
			}
			
			$scope.touch_scrolling.velocity.x *= 0.96;
			$scope.touch_scrolling.velocity.y *= 0.96;
			
			// console.log("TOUCH MOMENTUM!", $scope.touch_scrolling.velocity);
			
			const can_scroll = $scope.touch_scrolling.update_mobile_cursor($scope.touch_scrolling.velocity.x);
			if (can_scroll)
			{
				if ($scope.touch_scrolling.axis == 1)
				{
					timeline_element.scrollLeft -= $scope.touch_scrolling.velocity.x;
				}
				if ($scope.touch_scrolling.axis == 2)
				{
					document.documentElement.scrollTop -= $scope.touch_scrolling.velocity.y;
				}
			}
			
			const threshold = 0.2;
			if (($scope.touch_scrolling.axis == 1 && Math.abs($scope.touch_scrolling.velocity.x) < threshold) ||
				($scope.touch_scrolling.axis == 2 && Math.abs($scope.touch_scrolling.velocity.y) < threshold))
			{
				$scope.touch_scrolling.has_momentum = false;
				$scope.touch_scrolling.axis = false;
				return;
			}
			
			setTimeout(() => { $scope.touch_scrolling.update_momentum(); }, 7);
		},
	};
	
	angular.element($window).on('touchstart touchend', ($event) =>
	{
		if ($event.type == 'touchend')
		{
			if ($scope.touch_scrolling.active)
			{
				let identifier_found = false;
				for (const touch of $event.touches)
				{
					if (touch.identifier == $scope.touch_scrolling.identifier)
					{
						identifier_found = true;
						break;
					}
				}
				if (!identifier_found)
				{
					// console.log("STOPPING TOUCH SCROLL", $event);
					$scope.touch_scrolling.stop();
				}
			}
			return;
		}
		
		if ($event.type == 'touchstart')
		{
			if (!$event.target.closest('#timeline'))
				return;
			
			$scope.touch_scrolling.identifier = $event.changedTouches[0].identifier;
			$scope.touch_scrolling.position   = {
				x: $event.changedTouches[0].clientX,
				y: $event.changedTouches[0].clientY
			};
			
			$scope.touch_scrolling.initial = Utility.shallow_copy($scope.touch_scrolling.position);
			
			$scope.touch_scrolling.start();
			// console.log("STARTING TOUCH SCROLL", $event);
			
			$event.preventDefault();
		}
	});
	
	angular.element($window).on('touchmove', ($event) =>
	{
		let current_position = undefined;
		for (const touch of $event.touches)
		{
			if (touch.identifier == $scope.touch_scrolling.identifier)
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
			$scope.touch_scrolling.stop();
			return;
		}
		
		if (!$scope.touch_scrolling.active)
			return;
		
		$scope.touch_scrolling.update(current_position);		
		$event.preventDefault();
	});
	
	$scope.initialize_mobile_cursor = () =>
	{	
		const timeline_rect = timeline_element.getBoundingClientRect();
		const distance_left = timeline_element.scrollWidth - timeline_element.scrollLeft - timeline_rect.width;
		
		if (timeline_element.scrollLeft <= 0)
		{
			$scope.mobile_cursor = 0;
		}
		else if (distance_left <= 0)
		{
			$scope.mobile_cursor = 1;
		}
		else
		{
			$scope.mobile_cursor = 0.5;
		}
		
		if (Utility.mobile_mode())
		{
			$scope.set_indicator_opacity(1);
		}
	}
	
	// -------------------------------------------------------------------
	
	const force_hide_header_position = 120;
	
	angular.element($window).on('scroll', ($event) =>
	{
		$scope.update_timeline_indicator();
		
		const timeline_rect = timeline_element.getBoundingClientRect();
		SiteSettings.session_settings.force_hide_header = (timeline_rect.top < force_hide_header_position);
	});
	
	$scope.current_month_label_class = () =>
	{
		const timeline_rect = timeline_element.getBoundingClientRect();
		if (timeline_rect.top < force_hide_header_position)
		{
			return 'visible';
		}
		return '';
	}
	
	// -------------------------------------------------------------------
	
	$scope.jump_to_position = (target_month) =>
	{
		let timeline_target_entry = document.querySelector('#timeline-month-' + target_month);
		if (timeline_target_entry)
		{
			timeline_element.scrollLeft = 0;
			const timeline_rect = timeline_element.getBoundingClientRect();
			const rect = timeline_target_entry.getBoundingClientRect();
			timeline_element.scrollLeft = rect.left - timeline_rect.left - 200;
		}
	};
	
	// -------------------------------------------------------------------
	
	$scope.get_timeline_position = () =>
	{
		let visible_entry = undefined;
		
		const rect = timeline_element.getBoundingClientRect();
		const distance_left = timeline_element.scrollWidth - timeline_element.scrollLeft - rect.width;
		
		let first_entry = !$rootScope.settings.order_reversed ? 
			timeline_element.querySelector('.timeline-entry.month:first-child ng-include')?.closest('.month') :
			timeline_element.querySelector('.timeline-entry.month:last-child ng-include')?.closest('.month');
		
		let last_entry = $rootScope.settings.order_reversed ? 
			timeline_element.querySelector('.timeline-entry.month:first-child ng-include')?.closest('.month') :
			timeline_element.querySelector('.timeline-entry.month:last-child ng-include')?.closest('.month');
			
		// console.log(first_entry, last_entry);
		
		if (first_entry && timeline_element.scrollLeft < first_entry.getBoundingClientRect().width - 50)
		{
			visible_entry = first_entry;
		}
		else if (last_entry && distance_left < last_entry.getBoundingClientRect().width + 100)
		{
			visible_entry = last_entry;
		}
		else
		{
			let loaded_entries = Array.from(timeline_element.querySelectorAll('.timeline-entry.month ng-include'));
			if ($rootScope.settings.order_reversed)
			{
				loaded_entries = loaded_entries.reverse();
			}
			for (let entry_inner of loaded_entries)
			{
				const leeway = 250;
				let entry = entry_inner.closest('.month');
				
				if (Utility.isPartiallyVisibleInParent(timeline_element, entry, leeway))
				{
					visible_entry = entry;
					break;
				}
			}
		}
		
		if (!visible_entry)
			return false;
		
		return {
			current    : visible_entry.getAttribute('data-month-key'),
			month_name : visible_entry.getAttribute('data-month-name'),
			equivalent : visible_entry.getAttribute('data-equivalent-month'),
		}
	};
	
	$scope.update_timeline_position_param = () =>
	{
		let position = $scope.get_timeline_position();
		if (position !== false)
		{
			$scope.timeline_settings.target_month = position.current;
			$scope.timeline_settings.position     = position;
			
			$scope.current_month_label = position.month_name;
			
			LocationKeys.set('timeline_position', position.current);
		}
	};
	
	if (params.timeline_position !== undefined)
	{
		$scope.jump_to_position(params.timeline_position);
		$scope.update_timeline_position_param();
	}
	else
	{
		window.scrollTo(0, 0);
	}
	
	$scope.position_update_timeout = undefined;
	$scope.$on("$includeContentLoaded", function(event, templateName)
	{
		if ($scope.position_update_halted)
			return;
		
		if ($rootScope.settings.order_reversed)
		{
			$timeout.cancel($scope.position_update_timeout);
			$scope.position_update_timeout = $timeout(() => 
			{
				$scope.update_timeline_position_param();
			}, 150);
		}
		else
		{
			$scope.update_timeline_position_param();
		}
	});
	
	// -------------------------------------------------------------------
	
	$scope.current_day = {
		hovered_day : undefined,
		month_elem  : undefined,
		event_data  : undefined,
		hovered_ids : {},
	};
	
	$scope.set_indicator_opacity = (opacity) =>
	{
		indicator_line.style.opacity = opacity;
		date_highlight.style.opacity = opacity;
		date_tooltip.style.opacity = opacity;
	};
	$scope.get_indicator_opacity = () =>
	{
		return indicator_line.style.opacity;
	};
	
	$scope.unhighlight_everything = () =>
	{
		for (const [category, category_ids] of Object.entries($scope.current_day.hovered_ids))
		{
			for (const item_id of category_ids)
			{
				Utility.removeClass(hovered_item_class_format.format(category, item_id), 'hovered');
			}
		}
		$scope.current_day.hovered_ids = {};
		
		if ($scope.current_day.month_elem)
		{
			for (let day = 1; day <= 31; day++)
			{
				angular.element($scope.current_day.month_elem).removeClass(hovered_day_format.format(day));
			}
		}
		
		$scope.current_day.hovered_day = undefined;
		
		if ($scope.hovered_idol_id !== undefined)
		{
			$scope.$apply(() =>
			{
				$scope.hovered_idol_id = undefined;
			});
		}
	};
	
	$scope.restore_highlights = () =>
	{
		// Must be unset so timeline indicator update sees a changed date
		$scope.current_day.hovered_day = undefined;
		$scope.update_timeline_indicator();
		$scope.set_indicator_opacity(1);	
	}
	
	$scope.update_timeline_indicator = () =>
	{
		if (!$scope.mouse.target || !$scope.mouse.target.closest)
			return;
		
		if ($scope.grab_scroll.active || $scope.grab_scroll.has_momentum)
			return;
		
		let timeline_members = $scope.mouse.target.closest('.timeline-members');
		if (timeline_members)
		{
			$scope.set_indicator_opacity(0);
			$scope.unhighlight_everything();
			return;
		}
		else if (indicator_line.style.opacity == 0 && $scope.current_day.hovered_day !== undefined 
			   && $scope.current_day.hovered_day >= 1 && $scope.current_day.hovered_day <= $scope.current_day.month_days)
		{
			$scope.set_indicator_opacity(1);
		}
		else if (indicator_line.style.opacity == 0 && Utility.mobile_mode())
		{
			$scope.set_indicator_opacity(1);
		}
		
		let timeline_month = $scope.mouse.target.closest('.month');
		if (!timeline_month)
			return;
		
		let hovered_idol_id = undefined;
		let idol_row = $scope.mouse.target.closest('.idol-row');
		if (idol_row)
		{
			hovered_idol_id = idol_row.getAttribute('data-idol-id');
		}
		if ($scope.hovered_idol_id != hovered_idol_id)
		{
			$scope.$apply(() =>
			{
				$scope.hovered_idol_id = hovered_idol_id;
			});
		}
		
		const doc = document.documentElement;
		const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
		
		const month_key    = timeline_month.getAttribute('data-month-key');
		const month_days   = parseInt(timeline_month.getAttribute('data-month-days'));
		const month_start  = parseInt(timeline_month.getAttribute('data-month-start'));
		const month_number = parseInt(timeline_month.getAttribute('data-month-number'));
		const month_name   = timeline_month.getAttribute('data-month-name');
		
		const timeline_rect = timeline_element.getBoundingClientRect();
		const timeline_month_rect = timeline_month.getBoundingClientRect();
		
		const relative_x  = $scope.mouse.page.x - timeline_month_rect.left;
		const day_width   = timeline_month_rect.width / month_days;
		
		let hovered_day;
		let offset_day;
		
		const timeline_thumbnail = $scope.mouse.target.closest('.thumbnail');
		if (!timeline_thumbnail || Utility.mobile_mode())
		{
			$scope.autoscroll.disable = false;
			
			offset_day = Math.floor(relative_x / day_width) + month_start;
			hovered_day = offset_day;
			if ($rootScope.settings.order_reversed)
			{
				hovered_day = month_days - offset_day + 1;
			}
			
			indicator_line.style.left    = ($scope.mouse.absolute.x - timeline_rect.left - 1) + 'px';
			date_tooltip.style.left      = ($scope.mouse.absolute.x) + 'px';
		}
		else
		{
			$scope.autoscroll.disable = true;
			
			hovered_day = parseInt(timeline_thumbnail.getAttribute('data-month-day'));
			offset_day = hovered_day;
			if ($rootScope.settings.order_reversed)
			{
				offset_day  = month_days - hovered_day + 1;
			}
			
			let pos = ((offset_day - month_start) * day_width + day_width / 2 - timeline_rect.left + timeline_month_rect.left)
			
			indicator_line.style.left = pos + 'px';
			// date_tooltip.style.left   = (timeline_month_rect.left + (offset_day - month_start) * day_width + day_width / 2) + 'px';
			date_tooltip.style.left = (pos + timeline_rect.left) + 'px';
		}
		
		if (hovered_day < 1 || hovered_day > (month_days + month_start))
		{
			$scope.set_indicator_opacity(0);
		}
		
		if (!Utility.mobile_mode())
		{
			const distance_to_view_top    = Math.max(0, timeline_rect.top);
			const distance_to_view_bottom = (doc.scrollHeight - doc.clientHeight - scroll_top);
			
			const timeline_view_height    = Math.min(doc.clientHeight, timeline_rect.bottom) - Math.max(0, timeline_rect.top);
			
			if ($scope.mouse.absolute.y > doc.clientHeight * (0.48 + (distance_to_view_top / doc.clientHeight)))
			{
				const margin = timeline_view_height * 0.12;
				date_tooltip.style.top    = (distance_to_view_top + margin) + 'px';
				date_tooltip.style.bottom = 'auto';
			}
			else
			{
				const margin = timeline_view_height * 0.08;
				date_tooltip.style.top    = 'auto';
				date_tooltip.style.bottom = (Math.max(50, Math.max(0, 200 - distance_to_view_bottom) + margin)) + 'px';
			}
		}
			
		date_highlight.style.left   = ((offset_day - month_start) * day_width - timeline_rect.left + timeline_month_rect.left) + 'px';
		
		// If hovered day has changed do some updating
		if (hovered_day != $scope.current_day.hovered_day)
		{
			if ($scope.current_day.month_elem)
			{
				let class_name = hovered_day_format.format($scope.current_day.hovered_day);
				angular.element($scope.current_day.month_elem).removeClass(class_name);
			}
			let class_name = hovered_day_format.format(hovered_day);
			angular.element(timeline_month).addClass(class_name);
		
			$scope.current_day.hovered_day = hovered_day;
			$scope.current_day.month_key   = month_key;
			$scope.current_day.month_days  = month_days;
			$scope.current_day.month_start = month_start;
			$scope.current_day.month_name  = month_name;
			$scope.current_day.month_elem  = timeline_month;
			$scope.current_day.event_data  = undefined;
			
			let tooltip_data = {
				current_date  : date_format.format(Utility.ordinalize(hovered_day), month_name),
				events        : [],
				banners       : [],
				launch_day    : false,
				birthdays     : [],
			};
			
			if (timeline_month.matches(':first-child'))
			{
				if ($rootScope.settings.global_dates && hovered_day == 25)
				{
					tooltip_data.launch_day = 'Global';
				}
				else if (!$rootScope.settings.global_dates && hovered_day == 26)
				{
					tooltip_data.launch_day = 'Japanese';
				}
			}
			
			// --------------------------------------------------------------------------------------
			
			const tooltip_categories = ['events', 'banners'];
			let hovered_ids = {
				'events'  : [],
				'banners' : [],
			};
			
			for (const category of tooltip_categories)
			{
				const item_ids  = timeline_month.getAttribute('data-' + category).split(',');
				for (const item_id of item_ids)
				{
					if (!$scope.timeline_data[category][item_id])
						continue
					
					const item_data = Utility.deep_copy($scope.timeline_data[category][item_id]);
					
					const start = Utility.zip_isodate(item_data.timespan.start[1]);
					const end   = Utility.zip_isodate(item_data.timespan.end[1]);
					
					if ((start.month == end.month && (hovered_day >= start.day && hovered_day <= end.day)) ||
						(start.month != end.month && (
							(month_number == start.month && hovered_day >= start.day) ||
							(month_number == end.month   && hovered_day <= end.day))
						))
					{
						hovered_ids[category].push(item_id);
						
						item_data.timespan.start[1] = start;
						item_data.timespan.end[1] = end;
						
						tooltip_data[category].push(item_data);
						
						if (tooltip_data[category].length > 1)
						{
							tooltip_data[category].sort((a, b) =>
							{
								const a_value = a.timespan.start[1].year * 10000 + a.timespan.start[1].month * 100 + a.timespan.start[1].day;
								const b_value = b.timespan.start[1].year * 10000 + b.timespan.start[1].month * 100 + b.timespan.start[1].day;
								return a_value - b_value;
							});
						}
					}
				}
				
				if ($scope.current_day.hovered_ids[category] === undefined ||
					!Utility.arrays_equal(hovered_ids[category], $scope.current_day.hovered_ids[category]))
				{
					if ($scope.current_day.hovered_ids[category] !== undefined)
					{
						for (const item_id of $scope.current_day.hovered_ids[category])
						{
							Utility.removeClass(hovered_item_class_format.format(category, item_id), 'hovered', 'hovered');
						}
					}
					for (const item_id of hovered_ids[category])
					{
						Utility.addClass(hovered_item_class_format.format(category, item_id), 'hovered', 'hovered');
					}
					$scope.current_day.hovered_ids[category] = hovered_ids[category];
				}
			}
			
			// --------------------------------------------------------------------------------------
			
			for (const member of Member.get_month_birthdays(month_number))
			{
				if (member.birthday.day == hovered_day)
				{
					tooltip_data.birthdays.push(member);
				}
			}
			// for (const [id, member] of Object.entries(Member.members_ordered))
			// {
			// 	// if (member.birthday.day % 5 == hovered_day % 5)
			// 	if (member.id in member_birthday_phrase)
			// 	{
			// 		tooltip_data.birthdays.push(member);
			// 	}
			// }
			
			// --------------------------------------------------------------------------------------
			
			$scope.$apply(() => {
				$scope.tooltip_data = tooltip_data;
			});
		}
		
		if ($scope.mouse.absolute.x > (doc.clientWidth * 0.66))
		{
			const date_label_rect = date_tooltip.getBoundingClientRect();
			date_tooltip.style.marginLeft = -(date_label_rect.right - date_label_rect.left - 2) + 'px';
		}
		else
		{
			date_tooltip.style.marginLeft = 0;
		}
	}
	
	$scope.$on('keydown', (_, e) =>
	{
		if (e.repeat || e.ctrlKey || e.altKey || e.metaKey) return;
		
		if (e.keyCode == 27) // ESC-key
		{
			if ($scope.autoscroll.active)
			{
				e.preventDefault();
				$scope.autoscroll.stop();
			}
		}
		
		if (e.keyCode == 69) // E-key
		{
			e.preventDefault();
			$rootScope.settings.timeline_show_events = !$rootScope.settings.timeline_show_events;
			return;
		}
		
		if (e.keyCode == 66) // B-key
		{
			e.preventDefault();
			$rootScope.settings.timeline_show_banners = !$rootScope.settings.timeline_show_banners;
			return;
		}
		
		if (e.keyCode == 70) // F-key
		{
			e.preventDefault();
			$scope.timeline_settings.display_mode = Utility.wrap_value(
				$scope.timeline_settings.display_mode + (e.shiftKey ? -1 : 1),
				CardDisplayMode.SHOW_ALL, CardDisplayMode.SHOW_SR_ONLY);
			return;
		}
		
		if (!e.shiftKey)
		{
			if (e.keyCode == 82) // R-key
			{
				$scope.timeline_settings.display_mode       = CardDisplayMode.SHOW_ALL;
				$rootScope.settings.timeline_show_events    = true;
				$rootScope.settings.timeline_show_banners   = true;
				return;
			}
		}
	});
	
	$scope.set_indicator_opacity(0);
	
	$scope.initialize_mobile_cursor();
	
	// ----------------------
	
	$scope.loading = false;
	angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	
});
