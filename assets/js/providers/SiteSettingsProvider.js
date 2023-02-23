
app.provider('SiteSettings', function SiteSettingsProvider()
{
	var $this = this;

    this.settings = {
    	saved_settings : {
			use_idolized_thumbnails : SiteStorage.get('use_idolized_thumbnails', true),
			order_reversed          : SiteStorage.get('order_reversed', false),
			highlight_source        : SiteStorage.get('highlight_source', '0'),
			show_tooltips           : SiteStorage.get('show_tooltips', true),
			global_dates            : SiteStorage.get('global_dates',false),
			collapsed               : SiteStorage.get('collapsed', false),
			hide_empty_rows         : SiteStorage.get('hide_empty_rows', false),
			dark_mode               : SiteStorage.get('dark_mode', window.matchMedia("(prefers-color-scheme: dark)").matches),
			disable_motion          : SiteStorage.get('disable_motion', window.matchMedia("(prefers-reduced-motion)").matches),
			
			
			timeline_show_events    : SiteStorage.get('timeline_show_events', true),
			timeline_show_banners   : SiteStorage.get('timeline_show_banners', true),
		},
		
		session_settings : {
			force_hide_header         : false, 
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
