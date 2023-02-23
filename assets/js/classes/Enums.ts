
class Group
{
	id: number;
	display_name: string;
	tag: string;
	
	constructor(id: number, tag: string, display_name: string)
	{
		this.id           = id;
		this.tag          = tag;
		this.display_name = display_name;
	}
	
	static Muse         = new Group(1, "muse",       "µ's");
	static Aqours       = new Group(2, "aqours",     "Aqours");
	static Nijigasaki   = new Group(3, "nijigasaki", "Nijigasaki");
};

class Birthday
{
	month: number;
	day: number;
	
	constructor(month: number, day: number)
	{
		this.month = month;
		this.day = day;
	}
};

class Member
{
	id: number;
	full_name;
	first_name;
	birthday;
	group: Group;
		
	constructor(id: number, full_name: string, birthday: Birthday, group: Group)
	{
		this.id         = id;
		this.full_name  = full_name;
		this.first_name = full_name.split(' ')[0];
		this.birthday   = birthday;
		this.group      = group;
	}
	
	static members_by_id: { [key: number]: Member };
	static members_ordered: Member[];
	static members_by_name: { [key: string]: Member };
	
	static get_members(group?: Group)
	{
		return Object.fromEntries(Object.entries(this)
			.filter(([key, obj] : [any, Member?]) => obj instanceof this && (group === undefined || group.id != obj.group.id))
			.map(([key, obj] : [string, Member]) => [obj.id, obj])
		);
	}
	
	// ------------ Otonokizaka / µ's ------------
	static Hanayo   = new Member(8,   "Hanayo Koizumi",     new Birthday( 1, 17),  Group.Muse);
	static Rin      = new Member(5,   "Rin Hoshizora",      new Birthday(11,  1),  Group.Muse);
	static Maki     = new Member(6,   "Maki Nishikino",     new Birthday( 4, 19),  Group.Muse);

	static Honoka   = new Member(1,   "Honoka Kousaka",     new Birthday( 8,  3),  Group.Muse);
	static Kotori   = new Member(3,   "Kotori Minami",      new Birthday( 9, 12),  Group.Muse);
	static Umi      = new Member(4,   "Umi Sonoda",         new Birthday( 3, 15),  Group.Muse);

	static Nozomi   = new Member(7,   "Nozomi Toujou",      new Birthday( 6,  9),  Group.Muse);
	static Eli      = new Member(2,   "Eli Ayase",          new Birthday(10, 21),  Group.Muse);
	static Nico     = new Member(9,   "Nico Yazawa",        new Birthday( 7, 22),  Group.Muse);

	// ------------ Uranohoshi / Aqours ------------
	static Hanamaru = new Member(107, "Hanamaru Kunikida",  new Birthday( 3,  4),  Group.Aqours);
	static Yoshiko  = new Member(106, "Yoshiko Tsushima",   new Birthday( 7, 13),  Group.Aqours);
	static Ruby     = new Member(109, "Ruby Kurosawa",      new Birthday( 9, 21),  Group.Aqours);

	static Chika    = new Member(101, "Chika Takami",       new Birthday( 8,  1),  Group.Aqours);
	static Riko     = new Member(102, "Riko Sakurauchi",    new Birthday( 9, 19),  Group.Aqours);
	static You      = new Member(105, "You Watanabe",       new Birthday( 4, 17),  Group.Aqours);

	static Kanan    = new Member(103, "Kanan Matsuura",     new Birthday( 2, 10),  Group.Aqours);
	static Dia      = new Member(104, "Dia Kurosawa",       new Birthday( 1,  1),  Group.Aqours);
	static Mari     = new Member(108, "Mari Ohara",         new Birthday( 6, 13),  Group.Aqours);

	// ------------ Nijigasaki ------------
	static Rina     = new Member(209, "Rina Tennouji",      new Birthday(11, 13),  Group.Nijigasaki);
	static Kasumi   = new Member(202, "Kasumi Nakasu",      new Birthday( 1, 23),  Group.Nijigasaki);
	static Shizuku  = new Member(203, "Shizuku Ousaka",     new Birthday( 4,  3),  Group.Nijigasaki);
	static Shioriko = new Member(210, "Shioriko Mifune",    new Birthday(10,  5),  Group.Nijigasaki);

	static Ayumu    = new Member(201, "Ayumu Uehara",       new Birthday( 3,  1),  Group.Nijigasaki);
	static Setsuna  = new Member(207, "Setsuna Yuuki",      new Birthday( 8,  8),  Group.Nijigasaki);
	static Ai       = new Member(205, "Ai Miyashita",       new Birthday( 5, 30),  Group.Nijigasaki);
	static Lanzhu   = new Member(212, "Lanzhu Zhong",       new Birthday( 2, 15),  Group.Nijigasaki);

	static Emma     = new Member(208, "Emma Verde",         new Birthday( 2,  5),  Group.Nijigasaki);
	static Kanata   = new Member(206, "Kanata Konoe",       new Birthday(12, 16),  Group.Nijigasaki);
	static Karin    = new Member(204, "Karin Asaka",        new Birthday( 6, 29),  Group.Nijigasaki);
	static Mia      = new Member(211, "Mia Taylor",         new Birthday(12,  6),  Group.Nijigasaki);
	
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
	static get_member_order(group?: Group)
	{
		if (group !== undefined)
		{
			return Member.member_order_by_group[group.id];
		}
		return Object.entries(Member.member_order_by_group)
			.flatMap(([group_id, members] : [string, Member[]]) => members);
	};
	
	static get_month_birthdays(month: number, day: number)
	{
		return Object.entries(Member.members_by_id)
			.filter(([id, member] : [string, Member]) => member.birthday.month == month)
			.map(([id, member] : [string, Member]) => member);
	};
	static find_by_birthday(month: number, day: number)
	{
		const birthdays = Object.entries(Member.members_by_id)
			.filter(([id, member] : [string, Member]) => member.birthday.month == month && member.birthday.day == day)
			.map(([id, member] : [string, Member]) => member);
			
		if (birthdays.length == 0)
			return false;
		
		if (birthdays.length == 1)
			return birthdays[0];
		
		return birthdays;
	};
};
Member.members_by_id   = Member.get_members();
Member.members_ordered = Member.get_member_order();
Member.members_by_name = Object.fromEntries(Member.members_ordered.map((member : Member) => [member.first_name.toLowerCase(), member]));

class Source
{
	id: number;
	display_name: string;
	
	constructor(id: number, display_name: string)
	{
		this.id   = id;
		this.display_name = display_name;
	}
	
	static sources_by_id : { [key: number]: Source };
	
	static get_sources()
	{
		return Object.fromEntries(Object.entries(this)
			.filter(([key, obj] : [string, Source]) => obj instanceof this));
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
	id: number;
	display_name: string;
	
	constructor(id: number, display_name: string)
	{
		this.id = id;
		this.display_name = display_name;
	}
	
	static types_by_id : { [key: number]: EventType };
	
	static get_types()
	{
		return Object.fromEntries(Object.entries(this)
			.filter(([key, obj] : [string, EventType]) => obj instanceof this));
	}
	
	static Story    = new EventType(1, "Story");
	static Exchange = new EventType(2, "Exchange");
};
EventType.types_by_id = EventType.get_types();


// class BannerType
// {
// 	id;
// 	display_name;
// 	source;
	
// 	constructor(id, display_name, source)
// 	{
// 		this.id = id;
// 		this.display_name = display_name;
// 		this.source = source;
// 	}
	
// 	static types_by_id;
	
// 	static get_types()
// 	{
// 		return Object.fromEntries(Reflect.ownKeys(this).map((key) => this[key])
// 			.filter((obj) => (obj !== undefined && obj instanceof this))
// 			.map((obj) => [obj.id, obj])
// 		);
// 	}
	
// 	static Spotlight = new BannerType(1, "Spotlight", Source.Spotlight);
// 	static Festival  = new BannerType(2, "Festival",  Source.Festival);
// 	static Party     = new BannerType(3, "Party",     Source.Party);
// 	static Other     = new BannerType(4, "Other",     Source.Unspecified);
// 	// static Gacha     = new BannerType(5, "Gacha",     Source.Gacha);
// };
// BannerType.types_by_id = BannerType.get_types();

