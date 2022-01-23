<?php

require "../bootstrap.php";

# ---------------------------------------------------------------

$data = [
	'dark_mode_class' => '',
];

$dark_mode_enabled = boolval(cookie('dark_mode_enabled', false));
if ($dark_mode_enabled === true)
{
	$data['dark_mode_class'] = 'dark-mode';
}

display_view("content_index.php", $data);
