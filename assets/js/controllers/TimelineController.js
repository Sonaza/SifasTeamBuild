
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

app.controller('TimelineController', function(
		$rootScope, $scope,
		$route, $routeParams,
		$location, $window, $timeout,
		RouteEvent, SiteSettings, LocationKeys)
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
	
	$scope.mobile_current_date_label = "";
	
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
		
		if ($scope.autoscrolling.is_active())
		{
			output.push('autoscrolling');
		}
		
		if ($scope.mouse_dragging.is_active())
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
	
	RouteEvent.element(window).on('mousemove', ($event) =>
	{
		if (!Utility.mobile_mode())
		{
			$scope.mouse.absolute.x = $event.clientX;
			$scope.mouse.absolute.y = $event.clientY;
			$scope.mouse.target     = $event.target;
			$scope.mouse.movement.x = $event.movementX;
			$scope.mouse.movement.y = $event.movementY;
		}
		
		$scope.update_timeline_indicator();
	});
	
	
	// ----------------------------------------------------------------------------
	
	$scope.hovering_timeline = false;
	
	$scope.touch_scrolling = new TimelineTouchScrolling($scope, $window, SiteSettings);
	$scope.mouse_dragging = new TimelineMouseDragging($scope, $window);
	$scope.autoscrolling = new TimelineMouseAutoscrolling($scope, $window);
	
	RouteEvent.element(window).on('mouseover mouseout', ($event) =>
	{
		$scope.$apply(() =>
		{
			$scope.hovering_timeline = 
				$event.target.closest('#timeline') !== null && 
				$event.target.closest('.timeline-members') === null;
		});
		
		if ($event.type == 'mouseout')
		{
			$scope.unhighlight_everything();
		}
	});
	
	// ----------------------------------------------------------------------------
	
	$scope.current_mobile_mode = Utility.mobile_mode();
	
	RouteEvent.element(window).on('resize', ($event) =>
	{
		$scope.autoscrolling.stop();
		
		$scope.hovering_timeline = false;
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
	}
	
	RouteEvent.element(timeline_element).on('scroll', ($event) =>
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
			left   : timeline_rect.left + timeline_members_rect.width + 5,
			width  : timeline_rect.width - timeline_members_rect.width - 5,
			height : timeline_rect.height,
		}
	}
	
	$scope.update_mobile_indicator = () =>
	{
		if ($scope.mobile_cursor === undefined)
		{
			$scope.initialize_mobile_cursor();
		}
		
		const cursor_rect = $scope.get_mobile_cursor_rect();
		
		const doc = document.documentElement;
		const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
		
		$scope.mouse.absolute.x = cursor_rect.left + $scope.mobile_cursor * cursor_rect.width;
		
		// Try to magic a position within the timeline element that's always on screen
		$scope.mouse.absolute.y = Math.max(100, Math.min(doc.clientHeight - 100, cursor_rect.top + cursor_rect.height / 2));
		
		$scope.mouse.target     = document.elementFromPoint($scope.mouse.absolute.x, $scope.mouse.absolute.y);
		
		$scope.mouse.movement.x = 0;
		$scope.mouse.movement.y = 0;
		
		$scope.update_timeline_indicator();
		$scope.update_timeline_position_param();
	}
	
	// -------------------------------------------------------------------
	
	const force_hide_header_position = 180;
	const flipped_mobile_tooltip_position = 280;
	
	RouteEvent.element(window).on('scroll', ($event) =>
	{
		$scope.update_timeline_indicator();
		
		const timeline_rect = timeline_element.getBoundingClientRect();
		SiteSettings.session_settings.force_hide_header = (timeline_rect.top < force_hide_header_position);
		
	});
	
	$scope.mobile_current_date_label_class = () =>
	{
		const timeline_rect = timeline_element.getBoundingClientRect();
		if (timeline_rect.top >= force_hide_header_position)
			return;
		
		if (CardTooltip.tooltipVisible)
			return;
		
		if (!$scope.touch_scrolling.is_active())
			return;
		
		const doc = document.documentElement;
		const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
		const distance_to_view_bottom = (doc.scrollHeight - doc.clientHeight - scroll_top);
		
		if (distance_to_view_bottom < flipped_mobile_tooltip_position)
		{
			return 'visible flipped';
		}
		
		return 'visible';
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
			
			// $scope.mobile_current_date_label = position.month_name;
			
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
	
	$scope.mobile_cursor_initialized = false;
	
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
		
		if ((Utility.mobile_mode() || Utility.mobile_lite_mode()))
		{
			if ($rootScope.settings.order_reversed)
			{
				$timeout.cancel($scope.mobile_cursor_initialize_timeout);
				$scope.mobile_cursor_initialize_timeout = $timeout(() => 
				{
					$scope.update_mobile_indicator();
					$scope.mobile_cursor_initialized = true;
				}, 150);
			}
			else
			{
				$timeout(() =>
				{
					$scope.update_mobile_indicator();
				});
				$scope.mobile_cursor_initialized = true;
			}
		}
	});
	
	// -------------------------------------------------------------------
	
	$scope.current_day = {
		hovered_day : undefined,
		month_elem  : undefined,
		event_data  : undefined,
		hovered_ids : {},
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
	
	$scope.indicator_visible_class = () =>
	{
		if (!Utility.mobile_mode())
		{
			if (!$scope.hovering_timeline)
				return;
			
			if ($scope.autoscrolling.is_active() || $scope.mouse_dragging.is_active())
				return;
		}
		else
		{
			if ($scope.mobile_cursor === undefined || !$scope.mobile_cursor_initialized)
				return;
		}
		
		return 'visible';
	}
	
	$scope.tooltip_visible_class = () =>
	{
		if (!Utility.mobile_mode())
		{
			if (!$scope.hovering_timeline)
				return;
			
			if ($scope.autoscrolling.is_active() || $scope.mouse_dragging.is_active())
				return;
		}
		else
		{
			if (CardTooltip.tooltipVisible)
				return;
			
			if ($scope.touch_scrolling.is_active())
				return;
			
			if ($scope.mobile_cursor === undefined || !$scope.mobile_cursor_initialized)
				return;
		}
		
		return 'visible';
	}
	
	$scope.tooltip_mobile_class = () =>
	{
		const output = [];
		
		const timeline_rect = timeline_element.getBoundingClientRect();
		if (timeline_rect.top > force_hide_header_position)
		{
			output.push('hidden');
		}
		
		const doc = document.documentElement;
		const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
		const distance_to_view_bottom = (doc.scrollHeight - doc.clientHeight - scroll_top);
		
		if (distance_to_view_bottom < flipped_mobile_tooltip_position)
		{
			output.push('flipped');
		}
		
		return output.join(' ');
	}
	
	$scope.set_indicator_anchors = (line_anchor, highlight_anchor, tooltip_anchor) =>
	{
		indicator_line.style.left = line_anchor.left + "px";
		date_highlight.style.left = highlight_anchor.left + "px";
		
		// if (!Utility.mobile_mode())
		if (document.documentElement.clientWidth > 900)
		{
			date_tooltip.style.left = tooltip_anchor.left + "px";
			
			if (tooltip_anchor.top)
			{
				date_tooltip.style.top    = tooltip_anchor.top + "px";
				date_tooltip.style.bottom = 'auto';
			}
			
			if (tooltip_anchor.bottom)
			{
				date_tooltip.style.top    = 'auto';
				date_tooltip.style.bottom = tooltip_anchor.bottom + "px";
			}
			
			if (tooltip_anchor.margin)
			{
				date_tooltip.style.marginLeft = tooltip_anchor.margin + "px";
			}
			else
			{
				date_tooltip.style.marginLeft = 0;
			}
		}
		else
		{
			date_tooltip.style.inset = '';
			date_tooltip.style.marginLeft = 0;
		}
	}
	
	$scope.update_timeline_indicator = () =>
	{
		if (!$scope.mouse.target || !$scope.mouse.target.closest)
			return;
		
		if ($scope.mouse_dragging.is_active() || $scope.autoscrolling.is_active())
			return;
		
		let timeline_members = $scope.mouse.target.closest('.timeline-members');
		if (timeline_members)
		{
			$scope.unhighlight_everything();
			return;
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
		
		const line_anchor      = {};
		const highlight_anchor = {};
		const tooltip_anchor   = {};
		
		const doc = document.documentElement;
		const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
		
		const month_key    = timeline_month.getAttribute('data-month-key');
		const month_days   = parseInt(timeline_month.getAttribute('data-month-days'));
		const month_start  = parseInt(timeline_month.getAttribute('data-month-start'));
		const month_number = parseInt(timeline_month.getAttribute('data-month-number'));
		const month_name   = timeline_month.getAttribute('data-month-name');
		
		const timeline_rect = timeline_element.getBoundingClientRect();
		const timeline_month_rect = timeline_month.getBoundingClientRect();
		
		const relative_x  = $scope.mouse.absolute.x - timeline_month_rect.left;
		const day_width   = timeline_month_rect.width / month_days;
		
		let hovered_day;
		let offset_day;
		
		const timeline_thumbnail = $scope.mouse.target.closest('.thumbnail');
		if (!timeline_thumbnail || Utility.mobile_mode())
		{
			$scope.autoscrolling.set_disabled(false);
			
			offset_day = Math.floor(relative_x / day_width) + month_start;
			hovered_day = offset_day;
			if ($rootScope.settings.order_reversed)
			{
				hovered_day = month_days - offset_day + 1;
			}
			
			line_anchor.left    = $scope.mouse.absolute.x - timeline_rect.left - 1;
			tooltip_anchor.left = $scope.mouse.absolute.x;
		}
		else
		{
			$scope.autoscrolling.set_disabled(true);
			
			hovered_day = parseInt(timeline_thumbnail.getAttribute('data-month-day'));
			offset_day = hovered_day;
			if ($rootScope.settings.order_reversed)
			{
				offset_day  = month_days - hovered_day + 1;
			}
			
			let pos = ((offset_day - month_start) * day_width + day_width / 2 - timeline_rect.left + timeline_month_rect.left)
			
			line_anchor.left    = pos;
			tooltip_anchor.left = pos + timeline_rect.left;
		}
		
		// if (hovered_day < 1 || hovered_day > (month_days + month_start))
		// {
		// 	$scope.set_indicator_opacity(0);
		// }
		
		if (!Utility.mobile_mode())
		{
			const distance_to_view_top    = Math.max(0, timeline_rect.top);
			const distance_to_view_bottom = (doc.scrollHeight - doc.clientHeight - scroll_top);
			
			const timeline_view_height    = Math.min(doc.clientHeight, timeline_rect.bottom) - Math.max(0, timeline_rect.top);
			
			if ($scope.mouse.absolute.y > doc.clientHeight * (0.48 + (distance_to_view_top / doc.clientHeight)))
			{
				const margin = timeline_view_height * 0.12;
				tooltip_anchor.top = distance_to_view_top + margin;
			}
			else
			{
				const margin = timeline_view_height * 0.08;
				tooltip_anchor.bottom = Math.max(50, Math.max(0, 200 - distance_to_view_bottom) + margin);
			}
		}
			
		highlight_anchor.left = ((offset_day - month_start) * day_width - timeline_rect.left + timeline_month_rect.left);
		
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
			
			$scope.mobile_current_date_label  = tooltip_data.current_date;
			
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
			
			// --------------------------------------------------------------------------------------
			
			$scope.$apply(() => {
				$scope.tooltip_data = tooltip_data;
			});
		}
		
		if (!Utility.mobile_mode() || Utility.mobile_lite_mode())
		{
			if ($scope.mouse.absolute.x > (doc.clientWidth * 0.66))
			{
				const date_label_rect = date_tooltip.getBoundingClientRect();
				tooltip_anchor.margin = -(date_label_rect.right - date_label_rect.left - 2);
			}
		}
		
		$scope.set_indicator_anchors(line_anchor, highlight_anchor, tooltip_anchor);
	}
	
	$scope.$on('keydown', (_, e) =>
	{
		if (e.repeat || e.ctrlKey || e.altKey || e.metaKey) return;
		
		if (e.keyCode == 27) // ESC-key
		{
			if ($scope.autoscrolling.is_active())
			{
				$scope.autoscrolling.stop();
				e.preventDefault();
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
	
	// $scope.set_indicator_opacity(0);
	
	// $scope.initialize_mobile_cursor();
	
	// ----------------------
	
	$scope.loading = false;
	angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	
});
