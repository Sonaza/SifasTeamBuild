
class CardTooltip
{
	static tooltipVisible = false;	
	static toggleTooltip = function($scope, $event, visible)
	{
		// No need to do anything if tooltip is already hidden
		if (visible === false && CardTooltip.tooltipVisible === false)
			return;
		
		if ($event !== undefined)
		{
			if (Utility.mobile_mode())
			{
				// Don't accept mouse events, prevents double firing
				if ($event.type == "mouseover" || $event.type == "mouseout")
					return;
				
				if (visible === false)
				{
					// Prevent closing of the tooltip when clicking on the tooltip text.
					// Only close if clicking outside or on the Kirara link
					if (!($event.target.closest('#card-tooltip') !== null &&
						  $event.target.closest('.card-tooltip-inner') === null))
					{
						return;
					}
				}
			}
			else
			{
				// Disable click events on desktop mode
				if ($event.type == 'click')
					return;
			}
		}
		
		let tooltip = document.querySelector("#card-tooltip");
		let tooltip_element = angular.element(tooltip);
		
		CardTooltip.tooltipVisible = visible;
		
		// Hide tooltip
		if (visible == false)
		{
			if (!Utility.mobile_mode())
			{
				tooltip.style.visibility = 'hidden';
				tooltip.style.top = '-999px';
				tooltip.style.left = '-999px';
				tooltip.style.right = 'auto';
				tooltip.style.bottom = 'auto';
			}
			
			tooltip_element.removeClass('visible');
			return;
		}
			
		// Happens when auto closing on resize
		if ($event === undefined || $scope === undefined)
		{
			tooltip_element.removeClass('visible');
			tooltip.style.inset = '';
			return;
		}
		
		tooltip_element.addClass('visible');
		
		tooltip.style.visibility = 'visible';
		
		let tooltipDataElement = $event.target.closest('.tooltip-data');
		
		const keys = [
			'card-data', 'card-status', 'anchoring', 
		];
		
		$scope.tooltip_data = Object.assign(...keys.flatMap((key) => {
			return {
				[key.replace(/-/g, '_')] : tooltipDataElement.getAttribute('data-' + key)
			}
		}));
		
		let append = (data, target_keys) =>
		{
			if (target_keys.length == 1)
			{
				$scope.tooltip_data[target_keys[0]] = data;
			}
			else
			{
				for (let index in data)
				{
					$scope.tooltip_data[target_keys[index]] = data[index];
				}
			}
		}
		
		$scope.tooltip_data.card_status = Number($scope.tooltip_data.card_status) || 1;
		
		let card_data;
		if ($scope.tooltip_data.card_status == 1)
		{
			let card_ordinal = $scope.tooltip_data.card_data;
			card_data = GLOBAL_TOOLTIP_DATA[card_ordinal];
			$scope.tooltip_data.member = Member.members_by_id[card_data['m']];
		}
		else
		{
			let member_id = parseInt($scope.tooltip_data.card_data);
			$scope.tooltip_data.member = Member.members_by_id[member_id];
		}
		
		if ($scope.tooltip_data.card_status == 1)
		{
			append(card_data['d'], ['card_ordinal', 'card_rarity', 'card_attribute', 'card_type']);
			append(card_data['t'], ['card_title_normal', 'card_title_idolized']);
			append(card_data['s'], ['card_source']);
			append(card_data['r'], ['card_release']);
			if ("e" in card_data) append(card_data['e'], ['card_event']);
		}
		
		if (Utility.mobile_mode())
		{
			tooltip.style.inset = '';
			return;
		}
		
		// ---------------------------------------------------------------
		
		let tooltip_rect = tooltipDataElement.getBoundingClientRect();
		
		const doc = document.documentElement;
		const scroll_top = (window.pageYOffset || doc.scrollTop) - (doc.clientTop || 0);
		
		if (!$scope.tooltip_data.anchoring)
			$scope.tooltip_data.anchoring = 0;
		$scope.tooltip_data.anchoring = parseInt($scope.tooltip_data.anchoring);
		
		let anchor = {
			flipped : false,
			offset  : {x: 0, y: 0},
		}
		switch ($scope.tooltip_data.anchoring)
		{
			// Default anchoring
			case 0:
				anchor.offset = ($scope.tooltip_data.card_status == 1 ? 
					{x: 15, y: -16} :
					{x: 15, y: -4}
				);
				anchor.flipped = (tooltip_rect.x > doc.clientWidth * 0.66);
			break;
			
			// Stats tooltip anchoring
			case 1:
				anchor.offset = {x: 25, y: -26};
			break;
			
			// Timeline anchoring
			case 2:
				anchor.flipped = (tooltip_rect.x > doc.clientWidth * 0.55);
				anchor.offset = {x: 30, y: -22};
			break;
		}
		
		tooltip.style.top = (tooltip_rect.top + scroll_top + anchor.offset.y) + 'px';
		
		if (anchor.flipped)
		{
			tooltip.style.right = (doc.clientWidth - tooltip_rect.left + anchor.offset.x) + 'px';
			tooltip.style.left = 'auto';
		}
		else
		{
			tooltip.style.left = (tooltip_rect.right + anchor.offset.x) + 'px';
			tooltip.style.right = 'auto';
		}
	}
	
}

