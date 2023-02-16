
class Group
{
	id;
	display_name;
	tag;
	
	constructor(id, tag, display_name)
	{
		this.id           = id;
		this.tag          = tag;
		this.display_name = display_name;
	}
	
	static Muse         = new Group(1, "muse",       "µ's");
	static Aqours       = new Group(2, "aqours",     "Aqours");
	static Nijigasaki   = new Group(3, "nijigasaki", "Nijigasaki");
};

class Member
{
	id;
	full_name;
	first_name;
	group;
		
	constructor(id, full_name, group)
	{
		this.id         = id;
		this.full_name  = full_name;
		this.first_name = full_name.split(' ')[0];
		this.group      = group;
	}
	
	static members_by_id;
	static members_ordered;
	
	static get_members(group = undefined)
	{
		return Object.fromEntries(Reflect.ownKeys(this).map((key) => this[key])
			.filter((obj) => (
				obj !== undefined && obj instanceof this && 
					(group === undefined || group.id != e.group.id)
			))
			.map((obj) => [obj.id, obj])
		);
	}
	
	// ------------ Otonokizaka / µ's ------------
	static Hanayo   = new Member(8,   "Hanayo Koizumi",     Group.Muse);
	static Rin      = new Member(5,   "Rin Hoshizora",      Group.Muse);
	static Maki     = new Member(6,   "Maki Nishikino",     Group.Muse);

	static Honoka   = new Member(1,   "Honoka Kousaka",     Group.Muse);
	static Kotori   = new Member(3,   "Kotori Minami",      Group.Muse);
	static Umi      = new Member(4,   "Umi Sonoda",         Group.Muse);

	static Nozomi   = new Member(7,   "Nozomi Toujou",      Group.Muse);
	static Eli      = new Member(2,   "Eli Ayase",          Group.Muse);
	static Nico     = new Member(9,   "Nico Yazawa",        Group.Muse);

	// ------------ Uranohoshi / Aqours ------------
	static Hanamaru = new Member(107, "Hanamaru Kunikida",  Group.Aqours);
	static Yoshiko  = new Member(106, "Yoshiko Tsushima",   Group.Aqours);
	static Ruby     = new Member(109, "Ruby Kurosawa",      Group.Aqours);

	static Chika    = new Member(101, "Chika Takami",       Group.Aqours);
	static Riko     = new Member(102, "Riko Sakurauchi",    Group.Aqours);
	static You      = new Member(105, "You Watanabe",       Group.Aqours);

	static Kanan    = new Member(103, "Kanan Matsuura",     Group.Aqours);
	static Dia      = new Member(104, "Dia Kurosawa",       Group.Aqours);
	static Mari     = new Member(108, "Mari Ohara",         Group.Aqours);

	// ------------ Nijigasaki ------------
	static Rina     = new Member(209, "Rina Tennouji",      Group.Nijigasaki);
	static Kasumi   = new Member(202, "Kasumi Nakasu",      Group.Nijigasaki);
	static Shizuku  = new Member(203, "Shizuku Ousaka",     Group.Nijigasaki);
	static Shioriko = new Member(210, "Shioriko Mifune",    Group.Nijigasaki);

	static Ayumu    = new Member(201, "Ayumu Uehara",       Group.Nijigasaki);
	static Setsuna  = new Member(207, "Setsuna Yuuki",      Group.Nijigasaki);
	static Ai       = new Member(205, "Ai Miyashita",       Group.Nijigasaki);
	static Lanzhu   = new Member(212, "Lanzhu Zhong",       Group.Nijigasaki);

	static Emma     = new Member(208, "Emma Verde",         Group.Nijigasaki);
	static Kanata   = new Member(206, "Kanata Konoe",       Group.Nijigasaki);
	static Karin    = new Member(204, "Karin Asaka",        Group.Nijigasaki);
	static Mia      = new Member(211, "Mia Taylor",         Group.Nijigasaki);
	
	static member_order_by_group = {
		[Group.Muse.id] : [
			Member.Hanayo, Member.Rin,    Member.Maki,
			Member.Honoka, Member.Kotori, Member.Umi,
			Member.Nozomi, Member.Eli,    Member.Nico,
		],

		[Group.Aqours.id] : [
			Member.Hanamaru, Member.Yoshiko, Member.Ruby, 
			Member.Chika,    Member.Riko,    Member.You, 
			Member.Kanan,    Member.Dia,     Member.Mari, 
		],

		[Group.Nijigasaki.id] : [
			Member.Rina,  Member.Kasumi,  Member.Shizuku, Member.Shioriko, 
			Member.Ayumu, Member.Setsuna, Member.Ai,      Member.Lanzhu, 
			Member.Emma,  Member.Kanata,  Member.Karin,   Member.Mia, 
		],
	};
	static get_member_order(group = undefined)
	{
		if (group !== undefined)
		{
			return Member.member_order_by_group[group.id];
		}
		return Object.entries(Member.member_order_by_group).flatMap((e, i) => { return e[1]; });
	};
	static get_member_order(group = undefined)
	{
		if (group !== undefined)
		{
			return Member.member_order_by_group[group.id];
		}
		return Object.entries(Member.member_order_by_group).flatMap((e, i) => { return e[1]; });
	};
};
Member.members_by_id   = Member.get_members();
Member.members_ordered = Member.get_member_order();
Member.members_by_name = Object.fromEntries(Member.members_ordered.map((e, i) => [e.first_name.toLowerCase(), e]));


class Source
{
	id;
	display_name;
	
	constructor(id, display_name)
	{
		this.id   = id;
		display_name = display_name;
	}
	
	static sources_by_id;
	
	static get_sources()
	{
		return Object.fromEntries(Reflect.ownKeys(this).map((key) => this[key])
			.filter((obj) => (obj !== undefined && obj instanceof this))
			.map((obj) => [obj.id, obj])
		);
	}
	
	static Unspecified = new Source(1, 'Initial');
	static Event       = new Source(2, 'Event');
	static Gacha       = new Source(3, 'Gacha');  // 4th index is for the deprecated gacha part 2 
	static Spotlight   = new Source(5, 'Spotlight');
	static Festival    = new Source(6, 'Festival');
	static Party       = new Source(7, 'Party');
};
Source.sources_by_id = Source.get_sources();


class EventType
{
	id;
	display_name;
	
	constructor(id, display_name)
	{
		this.id = id;
		this.display_name = display_name;
	}
	
	static types_by_id;
	
	static get_types()
	{
		return Object.fromEntries(Reflect.ownKeys(this).map((key) => this[key])
			.filter((obj) => (obj !== undefined && obj instanceof this))
			.map((obj) => [obj.id, obj])
		);
	}
	
	static Story    = new EventType(1, "Story");
	static Exchange = new EventType(2, "Exchange");
};
EventType.types_by_id = EventType.get_types();


class BannerType
{
	id;
	display_name;
	source;
	
	constructor(id, display_name, source)
	{
		this.id = id;
		this.display_name = display_name;
		this.source = source;
	}
	
	static types_by_id;
	
	static get_types()
	{
		return Object.fromEntries(Reflect.ownKeys(this).map((key) => this[key])
			.filter((obj) => (obj !== undefined && obj instanceof this))
			.map((obj) => [obj.id, obj])
		);
	}
	
	static Spotlight = new BannerType(1, "Spotlight", Source.Spotlight);
	static Festival  = new BannerType(2, "Festival",  Source.Festival);
	static Party     = new BannerType(3, "Party",     Source.Party);
	static Other     = new BannerType(4, "Other",     Source.Unspecified);
	// static Gacha     = new BannerType(5, "Gacha",     Source.Gacha);
};
BannerType.types_by_id = BannerType.get_types();

