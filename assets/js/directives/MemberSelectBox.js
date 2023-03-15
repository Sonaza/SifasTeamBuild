
app.directive('memberSelectBox', function($parse, $templateCache, $compile, $timeout,
	SiteSettings, RouteEvent)
{
	return {
		restrict: 'A',
		scope: {
			current_index:  '=filterIndex',
			current_member: '=filterMember',
		},
		controller: function($rootScope, $scope, $attrs, $transclude)
		{
			if (!($scope.current_member instanceof Member))
			{
				$scope.current_member = false;
				$scope.current_index = 0;
			}
			
			$scope.max_index = Member.members_ordered.length;
			
			$scope.select_box_options_opened = false;
			$scope.last_toggled = 0;
			$scope.toggleSelectBox = () =>
			{
				const now = new Date().getTime();
				if ((now - $scope.last_toggled) < 50) return;
				$scope.last_toggled = now;
				
				$scope.select_box_options_opened = !$scope.select_box_options_opened;
				if ($scope.select_box_options_opened)
				{
					// Lol wtf
					setTimeout($scope.keepSelectBoxOnScreen, 50);
					setTimeout($scope.keepSelectBoxOnScreen, 100);
					setTimeout($scope.keepSelectBoxOnScreen, 150);
				}
				SiteSettings.session_settings.disable_scrolling = $scope.select_box_options_opened;
				SiteSettings.session_settings.disable_keydown_event = $scope.select_box_options_opened;
				$scope.current_kb_search = '';
			}
			
			$scope.optionSelectedClass = (member_id) =>
			{
				if (($scope.current_index == 0 && member_id === -1) ||
					($scope.current_member.id === member_id))
				{
					return 'selected';
				}
				return '';
			}
			
			$scope.selectBoxOptionsClass = () =>
			{
				return $scope.select_box_options_opened ? 'opened': 'hidden';
			}
			
			$scope.chooseSelectOption = (member_id) =>
			{
				if (member_id === -1)
				{
					$scope.current_index = 0;
				}
				else
				{
					for (let i = 0; i < Member.members_ordered.length; i++)
					{
						if (Member.members_ordered[i].id === member_id)
						{
							$scope.current_index = i + 1;
							break;
						}
					}
				}
				$scope.toggleSelectBox();
				$scope.$parent.$broadcast('refresh-deferred-loads');
			}
			
			$scope.keepSelectBoxOnScreen = () =>
			{
				let e = document.querySelector('.member-select-options');
				if (!e) return;
				
				const view_width = document.documentElement.clientWidth;
				if (view_width < 900)
				{
					angular.element(e).css('margin-left', '0');
					return;
				}
				let rect = e.getBoundingClientRect();
				
				var style = e.currentStyle || window.getComputedStyle(e);
				let current_margin = parseFloat(style.marginLeft);
				
				let margin = Math.min((view_width - rect.right) - 20 + current_margin, 0);
				angular.element(e).css('margin-left', margin + "px");
			}
			RouteEvent.element(window).on('resize scroll', $scope.keepSelectBoxOnScreen);
			$scope.keepSelectBoxOnScreen();
			
			$scope.$watch('current_index', (current_index, old_index) =>
			{
				if (current_index == 0)
				{
					$scope.current_member = false;
				}
				else
				{
					$scope.current_member            = Member.members_ordered[current_index - 1];
				}
			});
			
			$scope.current_kb_search = '';
			
			$scope.getKeyboardSearchMatches = () =>
			{
				if ($scope.current_kb_search.length < 2)
					return false;
				
				const name_matches = [];
				const alias_matches = [];
				
				for (let i = 0; i < Member.members_ordered.length; i++)
				{
					const member = Member.members_ordered[i];
					const full_name = member.full_name.toLowerCase().replace(' ', '');
					
					const no_spaces = $scope.current_kb_search.toLowerCase().replace(' ', '');
					const regex = new RegExp(no_spaces);
					
					if (full_name.match(regex))
					{
						name_matches.push(member.id);
					}
					else
					{
						for (const alias of Member.member_aliases[member.id])
						{
							if (alias.match(regex))
							{
								alias_matches.push(member.id);
								break;
							}
						}
					}
				}
				
				
				if (name_matches.length > 0)
				{
					return name_matches;
				}
				if (alias_matches.length > 0)
				{
					return alias_matches;
				}
				return false;
			}
			
			$scope.highlightSearchMatches = () =>
			{
				const search_matches = $scope.getKeyboardSearchMatches();
				if (!(search_matches instanceof Array) || search_matches.length == 0)
					return;

				return search_matches.map((member_id) => 'match-' + member_id).join(' ');
			}
			
			$scope.selectFirstSearchMatch = () =>
			{
				const search_matches = $scope.getKeyboardSearchMatches();
				if (!(search_matches instanceof Array) || search_matches.length == 0)
					return;
				
				for (let i = 0; i < Member.members_ordered.length; i++)
				{
					if (search_matches[0] == Member.members_ordered[i].id)
					{
						$scope.current_index = i + 1;
						return;
					}
				}
			}
			
			$scope.$on('$locationChangeStart', function(event, next, current)
			{
				if ($scope.select_box_options_opened)
				{
					$scope.toggleSelectBox();
			    	event.preventDefault();
				}
			});
			
			RouteEvent.element(window).on('keydown', (e) =>
			{
				if (e.altKey || e.metaKey) return;
				if (e.ctrlKey && e.shiftKey) return;
				
				if ($scope.select_box_options_opened)
				{
					if (e.keyCode == 8) // Backspace
					{
						$scope.$apply(() =>
						{
							if (e.ctrlKey)
							{
								$scope.current_kb_search = '';
							}
							else
							{
								$scope.current_kb_search = $scope.current_kb_search.slice(0, -1);	
							}
						});
						
						e.preventDefault();
						e.stopPropagation();
						return;
					}
				}
				
				if (e.repeat) return;
				
				if ($scope.select_box_options_opened)
				{
					if (e.ctrlKey && e.keyCode == 65) // A-key
					{
						$scope.$apply(() =>
						{
							$scope.current_kb_search = '';
						});
						
						e.preventDefault();
						e.stopPropagation();
						return;
					}
					
					if (e.keyCode == 27) // ESC-key
					{
						$scope.$apply(() => 
						{
							$scope.toggleSelectBox();
						});
						e.preventDefault();
						return;
					}
					
					
					if (e.keyCode == 13) // Enter
					{
						$scope.$apply(() =>
						{
							$scope.selectFirstSearchMatch();
							$scope.toggleSelectBox();
						});
						e.preventDefault();
						e.stopPropagation();
						return;
					}
					
					if (e.key.length != 1)
						return;
					
					const char = e.key;
					if (!char.match(/[A-Za-z ]/))
						return;
					
					$scope.$apply(() =>
					{
						if ($scope.current_kb_search.length < 20)
						{
							if (char == ' ')
							{
								if ($scope.current_kb_search.length == 0)
									return;
								if ($scope.current_kb_search.substr(-1) == ' ')
									return;
							}
							
							$scope.current_kb_search += char;
						}
					});
					
					e.preventDefault();
					e.stopPropagation();
					return;
				}
				
				if (e.keyCode == 13) // Enter
				{
					$scope.$apply(() =>
					{
						if (!Utility.mobile_mode())
						{
							const doc = document.documentElement;
							const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
							console.log(scroll_top);
							if (scroll_top > 150)
							{
								window.scrollTo(0, 120);
							}
						}
						
						$scope.toggleSelectBox();
					});
					e.preventDefault();
					e.stopPropagation();
					return;
				}
				
				if (e.keyCode == 69) // E-key
				{
					e.preventDefault();
					e.stopPropagation();
					
					$scope.$apply(() =>
					{
						$scope.current_index += (e.shiftKey ? -1 : 1);
						if ($scope.current_index < 0)
						{
							$scope.current_index = $scope.max_index;
						}
						else if ($scope.current_index > $scope.max_index)
						{
							$scope.current_index = 0;
						}
					});
				}
			});
		},
		link: function ($scope, $element, $attrs)
		{
			$element.addClass('member-select-box');
			
			let template = $templateCache.get('member_select_box.html');
			if (template !== undefined)
			{
				$element.html(template);
				$compile($element.contents())($scope);
			}
		}
	}
})

