<?php


function post($key, $default = null)
{
	return array_key_exists($key, $_POST) ? trim($_POST[$key]) : $default;
}

function get($key, $default = null)
{
	return array_key_exists($key, $_GET) ? trim($_GET[$key]) : $default;
}

function cookie($key, $default = null)
{
	return array_key_exists($key, $_COOKIE) ? trim($_COOKIE[$key]) : $default;
}

// ==============================================================

$dark_mode_class = '';

$dark_mode_enabled = boolval(cookie('dark_mode_enabled', false));
if ($dark_mode_enabled === true)
{
	$dark_mode_class = 'dark-mode';
}

require "content_index.php";
