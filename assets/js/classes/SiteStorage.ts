
/******************************************************
/* Storage Utility
/*/
/*
declare module 'localforage'
{
	// Here you can define the types for the localforage module
	// based on its documentation or typings file.

	// For example, if you're using the default localforage instance,
	// you can define its methods like this:
	interface LocalForage
	{
		setItem<T>(key: string, value: T): Promise<void>;
		getItem<T>(key: string): Promise<T | null>;
		// ...
	}

	// If you're using named instances, you can declare them like this:
	// interface LocalForageNamedInstances {
	//   myInstance: LocalForage;
	//   // ...
	// }

	// Finally, you can export the localforage instance(s) or namespace(s):
	const localforage: LocalForage;
	// const localforageNamedInstances: LocalForageNamedInstances;
	export default localforage;
	// export { localforageNamedInstances };
}

interface LocalForage
{
	setItem<T>(key: string, value: T): Promise<void>;
	getItem<T>(key: string): Promise<T | null>;
	// ...
}
let localforage: LocalForage;*/

class SiteStorage
{
	
	static get = (key: string, default_value: any) =>
	{
		let value: string | null = window.localStorage.getItem(key);
		if (value === null)
		{
			return default_value;
		}
		
		let parsed: any = JSON.parse(value);
		console.log("SiteStorage get ", key, value, parsed)
		return parsed;
		
		// return {
		// 	'boolean'   : (v: string | boolean) => v == 'true' || v == true,
		// 	'number'    : Number,
		// 	'bigint'    : Number,
		// 	'string'    : String,
		// 	'symbol'    : () => console.warn('value type symbol'),
		// 	'function'  : () => console.warn('value type function'),
		// 	'object'    : () => console.warn('value type object'),
		// 	'undefined' : () => console.warn('value type undefined'),
		// }[typeof default_value](value);
	}

	static save = (key: string, value: any) =>
	{
		window.localStorage.setItem(key, JSON.stringify(value));
	}

	static save_all = (values: { [key: string]: any }) =>
	{
		for (let [key, value] of Object.entries(values))
		{
			window.localStorage.setItem(key, JSON.stringify(value));
		}
	}
	
}
