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

