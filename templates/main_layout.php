<!DOCTYPE html>
<html ng-app="app">
<head>
	<title ng-bind-html="title">SIFAS Card Rotations</title>
	<meta charset="utf-8">
	
	<meta name="description" content="Love Live SIF All Stars card rotations and related statistics.">

	<meta name="og:site_name" content="SIFAS Card Rotations">	
	<meta property="og:url" content="https://sifas-cards.sonaza.com">
	<meta property="og:type" content="website">
	<meta property="og:title" content="SIFAS Card Rotations">
	<meta property="og:description" content="Love Live SIF All Stars card rotations and related statistics.">
	<meta property="og:image" itemprop="image primaryImageOfPage" content="https://sifas-cards.sonaza.com/img/favicon_tile_256.png">

	<meta name="twitter:card" content="summary">
	<meta property="twitter:domain" content="sifas-cards.sonaza.com">
	<meta property="twitter:url" content="https://sifas-cards.sonaza.com">
	<meta name="twitter:title" itemprop="name" content="SIFAS Card Rotations">
	<meta name="twitter:description" itemprop="description" content="Love Live SIF All Stars card rotations and related statistics.">
	<meta name="twitter:image" content="https://sifas-cards.sonaza.com/img/favicon_tile_256.png">
	
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta http-equiv="x-ua-compatible" content="ie=edge">
	<meta name="mobile-web-app-capable" content="yes">
  	<meta name="apple-mobile-web-app-capable" content="yes">
  	<meta name="apple-mobile-web-app-status-bar-style" content="black">
  	<meta name="apple-mobile-web-app-title" content="SIFAS Card Rotations">
  	
{# {% for item in preloads %}
	<link rel="preload" href="{{ item['path'] }}" as="{{ item['type'] }}">{% endfor %}
	<link rel="preload" href="/js/vendor/angular/angular-combined.min.js" as="script">
	<link rel="preload" href="/css/fonts/Roboto-Regular-Latin.woff2" as="font" crossorigin="anonymous">
	<link rel="preload" href="/css/fonts/Roboto-Bold-Latin.woff2" as="font" crossorigin="anonymous">
	<link rel="preload" href="/css/fonts/Montserrat-Regular-latin.woff2" as="font" crossorigin="anonymous">
	<link rel="preload" href="/css/fonts/Montserrat-Bold-latin.woff2" as="font" crossorigin="anonymous"> #}
 	<link rel="stylesheet" href="/css/vendor/font-awesome/font-awesome.min.css" media="(max-width: 1100px), (hover: none)">
	<link rel="stylesheet" href="{{ cache_buster('/css/public.min.css') }}">
	
	<link rel="icon" href="/favicon.ico">
	<link rel="apple-touch-icon" href="/img/favicon_tile_180.png">
	<link rel="apple-touch-icon" href="/img/favicon_tile_256.png" sizes="256x256">
	<link rel="apple-touch-icon" href="/img/favicon_tile_512.png" sizes="512x512">
	<link rel="shortcut icon" href="/img/favicon_tile_192.png">
	<link rel="manifest" href="/manifest.json">
</head>
<body ng-controller="BaseController" class="no-js <?= $dark_mode_class; ?>" ng-class="[activeSettingsClass(), hiddenHeaderActive(), scrollDisabler()]" ng-keydown="keydown($event)" tabindex="0" scroll="scroll($event, diff)">
	<div id="header" class="{{ 'dev-build' | conditional_css(cmd_args.dev) }}">
		<div id="header-inner">
			<div class="desktop-header">
				<h2 ng-bind-html="title">
					SIFAS Card Rotations
				</h2>
			</div>
			<div class="mobile-header">
				<div class="sidebar-toggle burger" ng-mousedown="toggle($event, 'navigation_visible')" ng-class="sidebarToggleActive(navigation_visible)">
					<div class="innards"><i class="fa fa-bars"></i></div>
					<div class="innards"><i class="fa fa-times"></i></div>
				</div>
				<h2>
					SIFAS Card Rotations
				</h2>
				<div class="sidebar-toggle settings" ng-mousedown="toggle($event, 'settings_visible')" ng-class="sidebarToggleActive(settings_visible)">
					<div class="innards"><i class="fa fa-cog"></i></div>
					<div class="innards"><i class="fa fa-times"></i></div>
				</div>
			</div>
			{% if cmd_args.dev %}
				<div class="dev-build">
					DEV BUILD!
				</div>
			{% endif %}
		</div>
	</div>
	<div id="main-outer-wrapper">
		<div id="main-wrapper">
			<div id="side-nav" ng-mousedown="tap_unfocus($event)" ng-class="anySideBarToggleActive()">
				<div class="side-nav-inner">
					<div class="nav-wrapper unfocus-target" ng-class="sidebarToggleActive(navigation_visible)">
						<ul class="side-nav-ul" ng-controller="NavController">
							<li><a href="#/"             ng-class="classActive('/', true)">Home</a></li>
							<li class="spacer"></li>
							<li><a href="#/ur-rotations" ng-class="classActive('/ur-rotations')">UR Rotations</a></li>
							<li><a href="#/sr-sets"      ng-class="classActive('/sr-sets')">SR Sets</a></li>
							<li class="spacer"></li>
							<li><a href="#/festival"     ng-class="classActive('/festival')">Festival Rotations</a></li>
							<li><a href="#/party"        ng-class="classActive('/party')">Party Rotations</a></li>
							<li><a href="#/event"        ng-class="classActive('/event', true)">Event Rotations</a></li>
							<li class="spacer"></li>
							<li><a href="#/muse"         ng-class="classActive('/muse')">µ's Cards</a></li>
							<li><a href="#/aqours"       ng-class="classActive('/aqours')">Aqours Cards</a></li>
							<li><a href="#/nijigasaki"   ng-class="classActive('/nijigasaki')">Nijigasaki Cards</a></li>
							<li class="spacer"></li>
							<li><a href="#/event_cards[[ filter_options ]]"  ng-class="classActive('/event_cards', true)">Event Cards</a></li>
							<li><a href="#/banners[[ filter_options ]]"      ng-class="classActive('/banners', true)">Gacha Banners</a></li>
							<li><a href="#/stats"                            ng-class="classActive('/stats')">Card Stats</a></li>
							<li><a href="#/history"                          ng-class="classActive('/history')">Card History <span class="new-tag">[NEW]</span></a></li>
							<?php /* <span class="new-tag">[NEW]</span> */ ?>
						</ul>
					</div>
					<div class="settings-wrapper unfocus-target" ng-class="sidebarToggleActive(settings_visible)">
						<div class="settings ng-cloak">
							<h3 class="show-mobile">Settings</h3>
							<div pill-button model="settings.use_idolized_thumbnails">
								Idolized Art
							</div>
							<div pill-button model="settings.order_reversed">
								Newest First
							</div>
							<div>
								<select class="source-selector ng-cloak" ng-model="settings.highlight_source">
									<option disabled>&mdash; Source Highlight &mdash;</option>
									<option ng-repeat="option in highlight_options" ng-value="option.value">[[ option.label ]]</option>
								</select>
								<select class="source-selector" id="source-selector-loading" ng-if="loading">
									<option selected disabled>Loading...</option>
								</select>
							</div>
							<div pill-button model="settings.show_tooltips">
								Tooltips
							</div>
							<div pill-button model="settings.dark_mode">
								Dark Mode
							</div>
						</div>
					</div>
				</div>
			</div>
			<div id="main">
				<div id="main-inner">
					<div class="main-content" ng-view>
						<noscript>
							{{ include_page("templates/noscript_notice.html") }}
						</noscript>
					</div>
				</div>
				<div id="card-tooltip" ng-class="{'mobile-card-tooltip': is_in_mobile_mode()}" ng-click="dismissMobileTooltip($event)" data-card-tooltip="tooltip_data"></div>
			</div>
		</div>
	</div>
	<footer id="footer" ng-controller="FooterController">
		<div id="footer-top">
			<div class="footer-top-inner">
				<div style="width:25%">
					Website created by Sonaza
				</div>
				<div style="width:50%">
					For use with <a href="https://lovelive-as-global.com/" target="_blank" rel="noreferrer noopener">Love Live School Idol Festival All Stars</a>
				</div>
				<div style="width:25%">
					<a href="https://forms.gle/sMK7KSmXDsgmHrvH9" target="_blank" rel="noreferrer noopener">Send Feedback</a>
				</div>
			</div>
		</div>
		<div id="footer-bottom">
			<div class="data-update">
				Last data update on {{ last_data_update | format_datestring(long_month=False, with_utc_time=True) }}<span class="ng-cloak time-since-update" ng-bind="time_since('{{ last_data_update.isoformat() }}')"></span>
				&mdash;
				Data is retrieved from <a href="https://allstars.kirara.ca/" target="_blank">Kirara All Stars Card Database</a>
			</div>
			<div class="disclaimer">
				This website is not affiliated with Love Live!, Mynet Inc., SUNRISE Inc., Bushiroad Inc. or any other associated company.
			</div>
			<div class="render-info">
				Page rendered
				{% if cmd_args.auto %}
					automatically
				{% endif %} on {{ last_update | format_datestring(long_month=False, with_utc_time=True) }}<span class="ng-cloak time-since-update" ng-bind="time_since('{{ last_update.isoformat() }}')"></span>
			</div>
		</div>
	</footer>
	<script type="text/ng-template" id="pages/home.html">{{ include_page('public/pages/home.html', minify=True) }}</script>
	{% if cmd_args.dev %}
		<script src="/js/vendor/angular/angular.js"></script>
		<script src="/js/vendor/angular/angular-route.js"></script>
		<script src="/js/vendor/angular/angular-sanitize.js"></script>
		<script src="/js/vendor/angular/angular-cookies.js"></script>
	{% else %}
		{# <script src="/js/vendor/angular/angular.min.js"></script>
		<script src="/js/vendor/angular/angular-route.min.js"></script>
		<script src="/js/vendor/angular/angular-sanitize.min.js"></script> #}
		<script src="{{ cache_buster('/js/vendor/angular/angular-combined.min.js') }}"></script>
	{% endif %}
	<script src="{{ cache_buster('/js/public.js') }}"></script>
</body>
</html>
