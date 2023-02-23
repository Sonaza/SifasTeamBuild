
interface Point {
	x: number;
	y: number;
};

class Utility
{
	/******************************************************
	 * Site preferences
	 */
	 
	static mobile_lite_mode = () =>
	{
		return document.documentElement.clientWidth > 900
		       && window.matchMedia("(hover: none)").matches;
	}
	 
	static mobile_mode = () =>
	{
		return document.documentElement.clientWidth <= 900
		       || window.matchMedia("(hover: none)").matches
		       || window.matchMedia("(pointer: coarse)").matches;
	}

	static prefers_reduced_motion = () =>
	{
		return window.matchMedia("(prefers-reduced-motion)").matches;
	}
	
	/******************************************************
	 * String formatting
	 */
	
	static ordinalize = function(number: string | number)
	{
		number = Number(number)
		
		let suffix;
		if (11 <= (number % 100) && (number % 100) <= 13)
		{
			suffix = 'th'
		}
		else
		{
			suffix = ['th', 'st', 'nd', 'rd', 'th'][Math.min(number % 10, 4)]
		}
		return `${number}${suffix}`
	}
	
	static pluralize = function(value: number, singular: string, plural: string)
	{
		return new String(value) + " " + (value == 1 ? singular : plural);
	}
	
	static format_seconds = function(seconds_param: number)
	{
		const days = Math.floor(seconds_param / 86400);
		if (days > 0)
		{
			return Utility.pluralize(days, "day", "days");
		}
		
		const hours = Math.floor(seconds_param % 86400 / 3600);
		if (hours > 0)
		{
			return Utility.pluralize(hours, "hour", "hours");
		}
		
		const minutes = Math.floor(seconds_param % 86400 % 3600 / 60);
		if (minutes > 0)
		{
			return Utility.pluralize(minutes, "minute", "minutes");
		}
		
		const seconds = Math.floor(seconds_param % 86400 % 3600 % 60);
		return Utility.pluralize(seconds, "second", "seconds");
	}
	
	// Wraps a date based on the time only so that relative to the given `now`
	// the date becomes yesterday, today or tomorrow when crossing midnight.
	static wrap_date(now: Date, date_value: Date)
	{
		const hour = date_value.getHours();
		const minute = date_value.getMinutes();
		date_value = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hour, minute);
		
		const past   = new Date(date_value.getTime() - 24 * 3600 * 1000);
		const future = new Date(date_value.getTime() + 24 * 3600 * 1000);
		
		const diff_present = Math.abs((now.getTime() - date_value.getTime()) / 1000 / 60);
		const diff_past    = ((now.getTime() - past.getTime()) / 1000 / 60);
		const diff_future  = ((future.getTime() - now.getTime()) / 1000 / 60);
		
		if (diff_present < diff_past && diff_present < diff_future)
		{
			return date_value;
		}
		
		if (diff_past < diff_future)
		{
			return past;
		}
		else
		{
			return future;
		}
	}
	
	/******************************************************
	 * Viewport
	 */
	
	static isElementPartiallyInViewport = function(el: HTMLElement)
	{
		let style = window.getComputedStyle(el);
		if (style.display === 'none')
			return false;
		
	    let rect = el.getBoundingClientRect();
	    return (
	        rect.top >= -rect.height &&
	        rect.left >= -rect.width &&
	        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + rect.height &&
	        rect.right <= (window.innerWidth || document.documentElement.clientWidth) + rect.width
	    );
	}

	static isPartiallyVisibleInParent(parent: HTMLElement, child: HTMLElement, horizontal_leeway: number = 0)
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
	
	/******************************************************
	 * Styling
	 */
	
	static addClass(selector: string, class_name: string)
	{
		for (const el of Array.from(document.querySelectorAll(selector)))
		{
			el.classList.add(class_name);
		}
	}
	
	static removeClass(selector: string, class_name: string)
	{
		for (const el of Array.from(document.querySelectorAll(selector)))
		{
			el.classList.remove(class_name);
		}
	}
	
	/******************************************************
	 * Stuff
	 */
	
	static distance(a: Point, b: Point)
	{
		const diff_x = b.x - a.x;
		const diff_y = b.y - a.y;
		return Math.sqrt(diff_x * diff_x + diff_y * diff_y);
	}
	
	static shallow_copy(object_to_copy: object)
	{
		return Object.assign({}, object_to_copy);
	}
	
	static deep_copy(object_to_copy: object)
	{
		return structuredClone(object_to_copy);
	}
	 
	static cache_buster(path: string, buster_string: string)
	{
		let path_split = path.split('.');
		let path_end = path_split.pop();
		return '{}.{}.{}'.format(
			path_split.join(' '),
			buster_string,
			path_end
		);
	}
	
	static zip(keys: any[], values: any[])
	{
		return Object.assign({}, ...keys.flatMap(function(key, value_index)
		{
			return {[key] : values[value_index]};
		}));
	}
	
	static zip_isodate(date: number[])
	{
		return Utility.zip(['year', 'month', 'day'], date);
	}
	
	static arrays_equal(a: any[], b: any[])
	{
		if (a === b) return true;
		if (a == null || b == null) return false;
		if (a.length !== b.length) return false;
		
		for (var i = 0; i < a.length; ++i)
		{
			if (a[i] !== b[i]) return false;
		}
		return true;
	}
	
	static abs_subtract(a: number, b: number)
	{
		return (Math.abs(a) - b) * (a < 0 ? -1 : 1);
	}
	
	static wrap_value(value: number, min_value: number, max_value: number)
	{
		if (value < min_value)
			return max_value;
		
		if (value > max_value)
			return min_value;
		
		return value;
	}

}

interface String {
  format(...args: any[]): string;
}

String.prototype.format = function ()
{
	var i = 0, args = arguments;
	return this.replace(/{}/g, function ()
	{
		return typeof args[i] != 'undefined' ? args[i++] : '';
	});
};
