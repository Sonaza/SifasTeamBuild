
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

app.controller('TimelineController', function($rootScope, $scope, $route, $routeParams, $location, $window, $timeout, LocationKeys)
{
	const date_format = '{} {}';
	const hovered_day_format = 'day-hovered-{}';
	const hovered_item_class_format = '.tl-{}-id-{}';

	const CardDisplayMode =
	{
		SHOW_ALL     : 0,
		SHOW_UR_ONLY : 1,
		SHOW_SR_ONLY : 2,
	}
	
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
		if ($scope.hovered_idol_id)
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
		
		return output.join(' ');
	}
	
	// ---------------------------------------------------------
	
	let timeline_element = document.querySelector('#timeline');
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
	
	$scope.set_indicator_opacity(0);
	
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
		if ($event.button != 1) // Middle mouse
			return;
		
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
	});
	
	angular.element($window).on('resize', ($event) =>
	{
		$scope.autoscroll.stop();
		$scope.set_indicator_opacity(0);
		$scope.unhighlight_everything();
		date_tooltip.style.left = undefined;
		date_tooltip.style.top = undefined;
		date_tooltip.style.bottom = undefined;
		date_tooltip.style.marginLeft = undefined;
	});
	
	angular.element(timeline_element).on('mouseover mouseout', ($event) =>
	{
		let timeline_members = $event.target.closest('.timeline-members');
		if (timeline_members)
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
	
	$scope.current_day = {
		'hovered_day' : undefined,
		'month_elem'  : undefined,
		'event_data'  : undefined,
		'hovered_ids' : {},
	};
	
	$scope.mouse = {
		absolute : {x: 0, y: 0},
		page     : {x: 0, y: 0},
		target   : undefined,
		relative : (element) =>
		{
			const rect = element.getBoundingClientRect();
			return {
				x: $scope.mouse.absolute.x - rect.x,
				y: $scope.mouse.absolute.y - rect.y,
			}
		}
	};
	
	angular.element(timeline_element).on('mousemove', ($event) =>
	{
		$scope.mouse.absolute.x = $event.clientX;
		$scope.mouse.absolute.y = $event.clientY;
		$scope.mouse.page.x     = $event.pageX;
		$scope.mouse.page.y     = $event.pageY;
		$scope.mouse.target     = $event.target;
		
		$scope.update_timeline_indicator();
	});
	angular.element(timeline_element).on('scroll', ($event) =>
	{
		$scope.$broadcast('refresh-deferred-loads');
		$scope.update_timeline_indicator();
		$scope.update_timeline_position_param();
	});
	angular.element($window).on('scroll', ($event) =>
	{
		$scope.update_timeline_indicator();
	});
	
	let in_view = function(parent, child, horizontal_leeway)
	{
	    let parent_rect = parent.getBoundingClientRect();
	    let child_rect = child.getBoundingClientRect();
	    return (
	        child_rect.top    >= parent_rect.top  - child_rect.height &&
	        child_rect.left   >= parent_rect.left - child_rect.width + horizontal_leeway &&
	        child_rect.bottom <= parent_rect.top  + parent_rect.height + child_rect.height &&
	        child_rect.right  <= parent_rect.left + parent_rect.width  + child_rect.width
	    );
	};
	
	$scope.jump_to_changed = () =>
	{
		$scope.jump_to_position($scope.timeline_settings.target_month);
	};
	
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
				
				if (in_view(timeline_element, entry, leeway))
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
			equivalent : visible_entry.getAttribute('data-equivalent-month'),
		}
	};
	
	$scope.update_timeline_position_param = () =>
	{
		let position = $scope.get_timeline_position();
		// console.log("update_timeline_position_param", position);
		if (position !== false)
		{
			$scope.timeline_settings.target_month = position.current;
			$scope.timeline_settings.position     = position;
			
			// $timeout(() => 
			// {
				LocationKeys.set('timeline_position', position.current);
			// });
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
	
	$scope.update_timeline_indicator = () =>
	{
		if (!$scope.mouse.target)
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
		if (!timeline_thumbnail)
		{
			$scope.autoscroll.disable = false;
			
			offset_day = Math.floor(relative_x / day_width) + month_start;
			hovered_day = offset_day;
			if ($rootScope.settings.order_reversed)
			{
				hovered_day = month_days - offset_day + 1;
			}
			
			indicator_line.style.left    = ($scope.mouse.page.x - timeline_rect.left - 1) + 'px';
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
			
			date_highlight.style.left   = ((offset_day - month_start) * day_width - timeline_rect.left + timeline_month_rect.left) + 'px';
		
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
					
					const item_data = Object.assign({}, $scope.timeline_data[category][item_id]);
					
					const start = Utility.zip_isodate(item_data.timespan.start[1]);
					const end   = Utility.zip_isodate(item_data.timespan.end[1]);
					
					if ((start.month == end.month && (hovered_day >= start.day && hovered_day <= end.day)) ||
						(start.month != end.month && (
							(month_number == start.month && hovered_day >= start.day) ||
							(month_number == end.month   && hovered_day <= end.day))
						))
					{
						hovered_ids[category].push(item_id);
						
						if (category == 'events')
						{
							if (start.year == end.year)
							{
								item_data.timespan.banner.start[0] = item_data.timespan.banner.start[0].replace(start.year, '');
								item_data.timespan.event.start[0] = item_data.timespan.event.start[0].replace(start.year, '');
								item_data.timespan.banner.end[0] = item_data.timespan.banner.end[0].replace(start.year, '');
								item_data.timespan.event.end[0] = item_data.timespan.event.end[0].replace(start.year, '');
							}
						}
						
						tooltip_data[category].push(item_data);
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
				$scope.timeline_settings.display_mode     = CardDisplayMode.SHOW_ALL;
				$rootScope.settings.timeline_show_events  = true;
				$rootScope.settings.timeline_show_banners = true;
				return;
			}
		}
	});
	
	$scope.loading = false;
	angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	
});
