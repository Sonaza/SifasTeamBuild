<?php

require "../bootstrap.php";

# ---------------------------------------------------------------

const SITE_TITLE = 'SIFAS Card Rotations';

$data = [
	'dark_mode_class' => '',
	'preset_subtitle' => false,
	'site_title' => SITE_TITLE,
	'current_site_title' => SITE_TITLE,
];

$dark_mode_enabled = boolval(cookie('dark_mode_enabled', false));
if ($dark_mode_enabled === true)
{
	$data['dark_mode_class'] = 'dark-mode';
}

# ---------------------------------------------------------------

$subpage_titles = [
	'ur'            => 'UR Rotations',
	'sr'            => 'SR Sets',
	'festival'      => 'Festival Rotations',
	'party'         => 'Party Rotations',
	'events'        => 'Event Rotations',
	'muse'          => 'µ\'s Cards',
	'aqours'        => 'Aqours Cards',
	'nijigasaki'    => 'Nijigasaki Cards',
	'event_history' => 'Event History',
	'banners'       => 'Banner History',
	'stats'         => 'Card Stats',
	'history'       => 'Card History',
	'timeline'      => 'Timeline',
];

$request_uri = $_SERVER['REQUEST_URI'];
$request_uri = explode('?', $request_uri, 2)[0];
$request_uri = explode('/', $request_uri);
array_shift($request_uri);
if (count($request_uri) > 0)
{
	$current_subpage = strtolower(trim($request_uri[0]));
	if (array_key_exists($current_subpage, $subpage_titles))
	{
		$data['preset_subtitle'] = $subpage_titles[$current_subpage];
		
		$data['current_site_title'] = $data['preset_subtitle'] . " &mdash; " . SITE_TITLE;
	}
}

$data['request_uri'] = $_SERVER['REQUEST_URI'];

display_view("main_index.php", $data);
