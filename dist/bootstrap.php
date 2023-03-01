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




function load_view($view_name, $data = [])
{
	$view_file = '../views/' . $view_name;
	if (!file_exists($view_file))
	{
		throw new Exception("View file '$view_name' does not exist.");
	}
	
	foreach ($data as $key => $value)
	{
		${$key} = $value;
	}
	
	ob_start();
	include($view_file);
	return ob_get_clean();
}

function display_view($view_name, $data = [])
{
	$output = load_view($view_name, $data);
	if ($output !== false)
	{
		echo $output;
	}
	else
	{
		throw new Exception("Loading the view '$view_name' failed.");
	}
}

$_SECTION_STACK = [];
$_SECTIONS = [];

function section($section_name)
{
	global $_SECTION_STACK;
	global $_SECTIONS;
	
	if (array_key_exists($section_name, $_SECTIONS))
	{
		throw new Exception("Section '$section_name' already exists.");
	}
	
	if (in_array($section_name, $_SECTION_STACK))
	{
		throw new Exception("Section '$section_name' is already active.");
	}
	
	$_SECTION_STACK[] = $section_name;
	ob_start();
}

function endsection()
{
	global $_SECTION_STACK;
	global $_SECTIONS;
	
	if (count($_SECTION_STACK) == 0)
	{
		throw new Exception("No section is currently active.");
	}
	
	$section_name = array_pop($_SECTION_STACK);
	$_SECTIONS[$section_name] = ob_get_clean();
}

function yieldsection($section_name)
{
	global $_SECTIONS;
	
	if (!array_key_exists($section_name, $_SECTIONS))
	{
		throw new Exception("Section '$section_name' does not exist.");
	}
	
	echo $_SECTIONS[$section_name];
}

function check_section_stack()
{
	global $_SECTION_STACK;
	if (count($_SECTION_STACK) > 0)
	{
		throw new Exception("All sections were not closed!");
	}
}
