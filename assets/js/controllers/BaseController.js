
app.controller('BaseController', function($rootScope, $scope, $location, $timeout, $parse, $window, $cookies, SiteSettings, LocationKeys, SiteRoutes, SiteGlobals)
	{
		angular.element(document.querySelector("body")).removeClass('no-js');
		
		const url_options = LocationKeys.get();
		if (url_options.idolized !== undefined)
		{
			if (url_options.idolized === 'true' || url_options.idolized == 1)
			{
				$rootScope.settings.use_idolized_thumbnails = true;
			}
			else
			{
				$rootScope.settings.use_idolized_thumbnails = false;
			}
		}
		
		if (url_options.reverse !== undefined)
		{
			if (url_options.reverse === 'true' || url_options.reverse == 1)
			{
				$rootScope.settings.order_reversed = true;
			}
			else
			{
				$rootScope.settings.order_reversed = false;
			}
		}
		
		if (url_options.highlight !== undefined)
		{
			if (url_options.highlight in highlight_map)
			{
				$rootScope.settings.highlight_source = highlight_map[url_options.highlight];
			}
			else
			{
				for (const opt of highlight_options)
				{
					if (opt.value == url_options.highlight)
					{
						$rootScope.settings.highlight_source = opt.value;
						break;
					}
				}
			}
		}
		
		if (!($rootScope.settings.highlight_source in highlight_reverse_map))
		{
			$rootScope.settings.highlight_source = '0';
		}
		
		//////////////////////////////////////////////////
		
		$scope.highlight_options = highlight_options;
		$scope.activeSettingsClass = () =>
		{
			let output = [];
			
			if ($rootScope.settings.use_idolized_thumbnails)
			{
				output.push('use-idolized-thumbnails');
			}
			
			// if ($rootScope.settings.alt)
			// {
			// 	output.push('alt-view');
			// }
			
			if ($rootScope.settings.collapsed)
			{
				output.push('stats-collapsed-tables');
			}
			
			if ($rootScope.settings.hide_empty_rows)
			{
				output.push('stats-hide-empty-rows');
			}
			
			if ($rootScope.settings.order_reversed)
			{
				output.push('order-reversed');
			}
			
			if (!$rootScope.settings.show_tooltips)
			{
				output.push('hide-tooltips');
			}
			
			if ($rootScope.settings.dark_mode)
			{
				output.push('dark-mode');
			}
			
			if ($rootScope.settings.global_dates)
			{
				output.push('using_ww_dates');
			}
			
			if ($rootScope.settings.disable_motion)
			{
				output.push('disable-motion');
			}
			
			output.push('source-highlight-' + $rootScope.settings.highlight_source);
			if ($rootScope.settings.highlight_source != '0')
			{
				output.push('source-highlighting-active');
			}
			else
			{
				output.push('source-highlighting-inactive');
			}
			
			if ($scope.navigation_visible || $scope.settings_visible)
			{
				output.push('sidebar-open');
			}
			
			if (Utility.mobile_mode())
			{
				output.push('mobile-mode');
			}
			
			if (SiteSettings.session_settings.disable_scrolling)
			{
				output.push('no-scroll');
			}
			
			return output.join(' ');
		}
		
		// -------------------------------------------------------------
		// More settings
		
		$scope.settingsMouseEnter = () =>
		{
			if (Utility.mobile_mode())
				return;
			
			if ($scope.collapse_more_timeout)
				clearTimeout($scope.collapse_more_timeout);
			$scope.collapse_more_timeout = false;
		}
		
		$scope.settingsMouseLeave = () =>
		{
			if (Utility.mobile_mode())
				return;
			
			$scope.collapse_more_timeout = setTimeout(() => {
				$scope.more_settings_opened = false;
				$scope.$apply();
			}, 3000);
		}
		
		$scope.more_settings_opened = Utility.mobile_mode();
		$scope.open_more_settings = () =>
		{
			$scope.more_settings_opened = true;
		}
		
		$scope.isActive = (view_location, exact_match) =>
		{
			if (exact_match)
			{
				return $location.path() === view_location;
			}
			else
			{
				return $location.path().startsWith(view_location);
			}
		};
		
		// -------------------------------------------------------------
				
		$scope.$watch('$root.settings', function(bs, settings)
		{
			Utility.saveStorage($rootScope.settings);
			$timeout(() => {
				$scope.unfocus();
			}, 350);
			
			if (!$rootScope.settings.show_tooltips)
			{
				CardTooltip.toggleTooltip(undefined, undefined, false);
			}
			
			let expires = new Date();
			expires.setDate(expires.getDate() + 365);
			if ($rootScope.settings.dark_mode)
			{
				$cookies.put('dark_mode_enabled', 1, {
					expires: expires,
					samesite: 'strict',
				});
			}
			else
			{
				$cookies.put('dark_mode_enabled', 0, {
					expires: expires,
					samesite: 'strict',
				});
			}
		}, true);
		
		$scope.$watch('$root.settings.highlight_source', function(bs, settings)
		{
			let e = document.querySelector(".source-selector");
			angular.element(e).addClass('changed');
			$timeout(() => {
				angular.element(e).removeClass('changed');
			}, 200);
		});
		
		$scope.main_content_class = () =>
		{
			if (SiteSettings.route_settings.main_content_no_h_padding)
			{
				return 'no-h-padding';
			}
			return '';
		}
		
		$scope.navigation_visible = false;
		$scope.settings_visible = false;
		
		$scope.header_hidden = false;
		$scope.hiddenHeaderClass = () =>
		{
			if ($scope.navigation_visible || $scope.settings_visible)
			{
				return '';
			}
			
			if ($scope.header_hidden || SiteSettings.session_settings.force_hide_header)
			{
				return 'header-hidden';
			}
			
			return '';
		}
		
		$scope.scroll_accumulator = 0;
		$scope.scroll = (event, diff) =>
		{
			let doc = document.documentElement;
			const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
			if ($scope.header_hidden && scroll_top < 50)
			{
				$scope.scroll_accumulator = 0;
				$scope.header_hidden = false;
				return;
			}
			
			if ((diff < 0 && $scope.scroll_accumulator > 0) || (diff > 0 && $scope.scroll_accumulator < 0))
			{
				$scope.scroll_accumulator = 0;
			}
			
			$scope.scroll_accumulator += diff;
			
			if (diff > 0)
			{
				if ($scope.scroll_accumulator > 150)
				{
					$scope.header_hidden = true;
				}
			}
			else if (diff < 0)
			{
				if ($scope.scroll_accumulator < -200)
				{
					$scope.header_hidden = false;
				}
			}
		}
		
		$scope.toggle = ($event, variable_name) =>
		{
			let variable = $parse(variable_name);
			let value = variable($scope);
			
			$scope.navigation_visible = false;
			$scope.settings_visible = false;
			
			variable.assign($scope, !value);
			
			CardTooltip.toggleTooltip(undefined, undefined, false);
		}
		
		$scope.sidebarToggleActive = (value) => 
		{
			if (value)
			{
				return 'visible';
			}
		}
		
		$scope.anySideBarToggleActive = () =>
		{
			if ($scope.navigation_visible || $scope.settings_visible)
			{
				return 'sidebar-visible';
			}
		}
		
		$scope.unfocus = ($event) =>
		{
			$scope.navigation_visible = false;
			$scope.settings_visible = false;
			
			$scope.scroll_accumulator = 0;
			$scope.header_hidden = false;
		}
		
		$scope.tap_unfocus = ($event) =>
		{
			if (!$event) return;
			
			if ($event.target == $event.target.closest('#header'))
			{
				return;
			}
			
			if ($event.target == $event.target.closest('.unfocus-target') || 
				$event.target == $event.target.closest('#side-nav') || 
				$event.target == $event.target.closest('.side-nav-inner') || 
				$event.target == $event.target.closest('.side-nav-ul'))
			{
				$scope.unfocus();
			}
		}
		
		$scope.handle_expiry = function(next_url)
		{
			let now = new Date();
			let now_utc = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), now.getUTCHours(), now.getUTCMinutes(), now.getUTCSeconds()));
			
			if ($scope.page_loaded === undefined)
			{
				$scope.page_loaded = now_utc;
				
				let expiry_dates = [
					new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(),     6, 3, 0)),
					new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + 1, 6, 3, 0)),
				];
				for (const expiry of expiry_dates)
				{
					if (expiry < $scope.page_loaded)
						continue;
					
					$scope.page_expires = expiry;
					break;
				}
				
				console.info("This page was initially loaded on", $scope.page_loaded);
				console.info("This page will expire on", $scope.page_expires);
			}
			
			if (now_utc >= $scope.page_expires)
			{
				location.href = next_url;
				location.reload();
			}
		}
		
		$rootScope.$on("$routeChangeStart", function(event, next, current)
		{ 
			$scope.handle_expiry(next);
			$scope.unfocus();
		});
		
		$rootScope.$on('$routeChangeSuccess', (event) =>
		{
			const active_route = SiteRoutes.active_route();
			if (active_route.path !== '/')
			{
				const route_subtitle = active_route.get_subtitle();
				if (route_subtitle !== undefined)
				{
					$rootScope.title = active_route.title + " / " + route_subtitle + " &mdash; " + SiteGlobals.site_title;
				}
				else
				{
					$rootScope.title = active_route.title + " &mdash; " + SiteGlobals.site_title;
				}
			}
			else
			{
				$rootScope.title = SiteGlobals.site_title;
			}
			
			angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
		});
		
		$scope.keydown = ($event) =>
		{
			if ($event.repeat) return;
			
			if (!($event.repeat || $event.ctrlKey || $event.altKey || $event.metaKey))
			{
				if ($event.keyCode == 83) // S-key
				{
					for (let i in highlight_options)
					{
						if (highlight_options[i].value == $rootScope.settings.highlight_source)
						{
							$event.preventDefault();
							
							if (!$event.shiftKey)
							{
								let nextIndex = parseInt(i) + 1; // fuck javascript such a shitty language
							
								if (nextIndex < highlight_options.length)
								{
									$rootScope.settings.highlight_source = highlight_options[nextIndex].value;
								}
								else
								{
									$rootScope.settings.highlight_source = highlight_options[0].value;
								}
							}
							else
							{
								let prevIndex = parseInt(i) - 1; // fuck javascript such a shitty language
								if (prevIndex >= 0)
								{
									$rootScope.settings.highlight_source = highlight_options[prevIndex].value;
								}
								else
								{
									$rootScope.settings.highlight_source = highlight_options[highlight_options.length-1].value;
								}
							}
							return;
						}
					}
				}
				
				if (!$event.shiftKey)
				{
					if ($event.keyCode == 81) // Q-key
					{
						$event.preventDefault();
						$rootScope.settings.use_idolized_thumbnails = !$rootScope.settings.use_idolized_thumbnails;
						return;
					}
					
					if ($event.keyCode == 87) // W-key
					{
						$event.preventDefault();
						$rootScope.settings.order_reversed	 = !$rootScope.settings.order_reversed;
						return;
					}
					
					if ($event.keyCode == 84) // T-key
					{
						$event.preventDefault();
						$rootScope.settings.show_tooltips	 = !$rootScope.settings.show_tooltips;
						return;
					}
					
					if ($event.keyCode == 68) // D-key
					{
						$event.preventDefault();
						$rootScope.settings.global_dates	 = !$rootScope.settings.global_dates;
						return;
					}
					
					if ($event.keyCode == 82) // R-key
					{
						$event.preventDefault();
						$rootScope.settings.highlight_source        = '0';
						// $rootScope.settings.use_idolized_thumbnails = true;
						// $rootScope.settings.order_reversed          = false;
						// $rootScope.settings.global_dates            = false;
						// return;
					}
				}
			}
			
			$rootScope.$broadcast('keydown', $event);
			
			angular.element(document.querySelector("#source-selector-default")).remove();
		};
		
		angular.element(document.querySelectorAll(".ng-cloak")).removeClass('ng-cloak');
	}
)
