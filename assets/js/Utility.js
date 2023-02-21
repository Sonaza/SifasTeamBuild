
class Utility
{
	/******************************************************
	 * Storage Utility
	 */
	 
	static storageAvailable = (type) =>
	{
		var storage;
		try {
			storage = window[type];
			var x = '__storage_test__';
			storage.setItem(x, x);
			storage.removeItem(x);
			return true;
		}
		catch(e) {
			return e instanceof DOMException && (
				// everything except Firefox
				e.code === 22 ||
				// Firefox
				e.code === 1014 ||
				// test name field too, because code might not be present
				// everything except Firefox
				e.name === 'QuotaExceededError' ||
				// Firefox
				e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
				// acknowledge QuotaExceededError only if there's something already stored
				(storage && storage.length !== 0);
		}
	}
	
	static getStorage = (key, default_value) =>
	{
		if (!Utility.storageAvailable('localStorage'))
		{
			return default_value;
		}
		
		let value = window.localStorage.getItem(key);
		if (value === null || value === "null")
		{
			return default_value;
		}
		
		return {
			'boolean'   : (v) => v == 'true',
			'number'    : Number,
			'string'    : String,
			'undefined' : () => console.warn('value type undefined'),
		}[typeof default_value](value);
	}

	static saveStorage = (values) =>
	{
		if (!Utility.storageAvailable('localStorage'))
		{
			return;
		}
		
		for (let [key, value] of Object.entries(values))
		{
			window.localStorage.setItem(key, value);
		}
	}
	
	/******************************************************
	 * Site preferences
	 */
	 
	static mobile_mode = () =>
	{
		return document.documentElement.clientWidth <= 900
		       || window.matchMedia("(hover: none)").matches
		       || window.matchMedia("(any-hover: none)").matches
		       || window.matchMedia("(pointer: coarse)").matches;
	}

	static prefers_reduced_motion = () =>
	{
		return window.matchMedia("(prefers-reduced-motion)").matches;
	}
	
	/******************************************************
	 * String formatting
	 */
	
	static ordinalize = function(n)
	{
		n = parseInt(n)
		let suffix;
		if (11 <= (n % 100) && (n % 100) <= 13)
		{
			suffix = 'th'
		}
		else
		{
			suffix = ['th', 'st', 'nd', 'rd', 'th'][Math.min(n % 10, 4)]
		}
		return n + suffix;
	}
	
	static pluralize = function(value, s, p)
	{
		return new String(value) + " " + (value == 1 ? s : p);
	}
	
	static format_seconds = function(seconds_param)
	{
		let days = Math.floor(seconds_param / 86400);
		let hours = Math.floor(seconds_param % 86400 / 3600);
		let minutes = Math.floor(seconds_param % 86400 % 3600 / 60);
		let seconds = Math.floor(seconds_param % 86400 % 3600 % 60);
		
		if (days > 0)
		{
			return Utility.pluralize(days, "day", "days") + " ago";
		}
		
		if (hours > 0)
		{
			return Utility.pluralize(hours, "hour", "hours") + " ago";
		}
		
		if (minutes > 0)
		{
			return Utility.pluralize(minutes, "minute", "minutes") + " ago";
		}
		
		return Utility.pluralize(seconds, "second", "seconds") + " ago";
	}
	
	// Wraps a date based on the time only so that relative to the given `now`
	// the date becomes yesterday, today or tomorrow when crossing midnight.
	static wrap_date(now, date_value)
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
	
	static isElementPartiallyInViewport = function(el)
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

	static isPartiallyVisibleInParent(parent, child, horizontal_leeway = 0)
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
	
	static addClass(selector, class_name)
	{
		for (let el of document.querySelectorAll(selector))
		{
			el.classList.add(class_name);
		}
	}
	
	static removeClass(selector, class_name)
	{
		for (let el of document.querySelectorAll(selector))
		{
			el.classList.remove(class_name);
		}
	}
	
	/******************************************************
	 * Stuff
	 */
	 
	static distance(a, b)
	{
		const diff_x = b.x - a.x;
		const diff_y = b.y - a.y;
		return Math.sqrt(diff_x * diff_x + diff_y * diff_y);
	}
	
	static shallow_copy(object_to_copy)
	{
		return Object.assign({}, object_to_copy);
	}
	
	static deep_copy(object_to_copy)
	{
		return structuredClone(object_to_copy);
	}
	 
	static cache_buster(path, buster_string)
	{
		let path_split = path.split('.');
		let path_end = path_split.pop();
		return '{}.{}.{}'.format(
			path_split.join(' '),
			buster_string,
			path_end
		);
	}
	
	static zip(a, b)
	{
		return Object.assign(...a.flatMap(function(e, i) {
			return {[e] : b[i]};
		}));
	}
	
	static zip_isodate(date)
	{
		return Utility.zip(['year', 'month', 'day'], date);
	}
	
	static arrays_equal(a, b)
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
	
	static abs_subtract(a, b)
	{
		return (Math.abs(a) - b) * (a < 0 ? -1 : 1);
	}
	
	static wrap_value(value, min_value, max_value)
	{
		if (value < min_value)
			return max_value;
		
		if (value > max_value)
			return min_value;
		
		return value;
	}

}

String.prototype.format = function ()
{
	var i = 0, args = arguments;
	return this.replace(/{}/g, function ()
	{
		return typeof args[i] != 'undefined' ? args[i++] : '';
	});
};


// export default Utility;



