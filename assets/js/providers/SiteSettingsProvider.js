
app.provider('SiteSettings', function SiteSettingsProvider()
{
	var $this = this;

    this.settings = {
    	saved_settings : {
			use_idolized_thumbnails : Utility.getStorage('use_idolized_thumbnails', true),
			order_reversed          : Utility.getStorage('order_reversed', false),
			highlight_source        : Utility.getStorage('highlight_source', '0'),
			show_tooltips           : Utility.getStorage('show_tooltips', true),
			global_dates            : Utility.getStorage('global_dates',false),
			collapsed               : Utility.getStorage('collapsed', false),
			hide_empty_rows         : Utility.getStorage('hide_empty_rows', false),
			dark_mode               : Utility.getStorage('dark_mode', window.matchMedia("(prefers-color-scheme: dark)").matches),
			disable_motion          : Utility.getStorage('disable_motion', window.matchMedia("(prefers-reduced-motion)").matches),
			
			timeline_show_events    : Utility.getStorage('timeline_show_events', true),
			timeline_show_banners   : Utility.getStorage('timeline_show_banners', true),
		},
		
		session_settings : {
			force_hide_header         : false, 
			disable_scrolling         : false,
			disable_keydown_event     : false,
		},
		
		route_settings : {
			main_content_no_h_padding : false,
		},
	}
	
    this.$get = () =>
    {
        return $this.settings;
    }
});
