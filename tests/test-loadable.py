import sqlite3
import unittest
from pathlib import Path

EXT_PATH = "./dist/debug/robotstxt0"

GOOGLE_ROBOTSTXT = (
    Path(__file__).parent / "examples" / "google.com.robots.txt"
).read_text("utf-8")


def connect(ext):
    db = sqlite3.connect(":memory:")

    db.execute("create table base_functions as select name from pragma_function_list")
    db.execute("create table base_modules as select name from pragma_module_list")

    db.enable_load_extension(True)
    db.load_extension(ext)

    db.execute(
        "create temp table loaded_functions as select name from pragma_function_list where name not in (select name from base_functions) order by name"
    )
    db.execute(
        "create temp table loaded_modules as select name from pragma_module_list where name not in (select name from base_modules) order by name"
    )

    db.row_factory = sqlite3.Row
    return db


db = connect(EXT_PATH)


def explain_query_plan(sql):
    return db.execute("explain query plan " + sql).fetchone()["detail"]


def execute_all(sql, args=None):
    if args is None:
        args = []
    results = db.execute(sql, args).fetchall()
    return list(map(lambda x: dict(x), results))


FUNCTIONS = [
    "robotstxt_debug",
    "robotstxt_matches",
    "robotstxt_version",
]

MODULES = [
    "robotstxt_rules",
    "robotstxt_user_agents",
]


def spread_args(args):
    return ",".join(["?"] * len(args))


class TestRobotstxt(unittest.TestCase):
    def test_funcs(self):
        funcs = list(
            map(
                lambda a: a[0],
                db.execute("select name from loaded_functions").fetchall(),
            )
        )
        self.assertEqual(funcs, FUNCTIONS)

    def test_modules(self):
        modules = list(
            map(
                lambda a: a[0], db.execute("select name from loaded_modules").fetchall()
            )
        )
        self.assertEqual(modules, MODULES)

    def test_robotstxt_version(self):
        self.assertEqual(db.execute("select robotstxt_version()").fetchone()[0][0], "v")

    def test_robotstxt_debug(self):
        debug = db.execute("select robotstxt_debug()").fetchone()[0]
        self.assertEqual(len(debug.splitlines()), 2)

    def test_robotstxt_matches(self):
        robotstxt_matches = lambda *args: db.execute(
            "select robotstxt_matches(?, ?, ?)", args
        ).fetchone()[0]
        self.assertEqual(
            robotstxt_matches(GOOGLE_ROBOTSTXT, "Twitterbot", "/search"), 1
        )
        self.assertEqual(
            robotstxt_matches(GOOGLE_ROBOTSTXT, "Twitterbot", "/groups"), 0
        )

    def test_robotstxt_user_agents(self):
        robotstxt_user_agents = lambda *args: execute_all(
            "select * from  robotstxt_user_agents(?)", args
        )
        self.assertEqual(
            robotstxt_user_agents(GOOGLE_ROBOTSTXT),
            [
                {"name": "*", "rules": None, "source": 1},
                {"name": "AdsBot-Google", "rules": None, "source": 280},
                {"name": "Twitterbot", "rules": None, "source": 288},
                {"name": "facebookexternalhit", "rules": None, "source": 295},
            ],
        )

    def test_robotstxt_rules(self):
        robotstxt_rules = lambda *args: execute_all(
            "select * from  robotstxt_rules(?)", args
        )

        self.assertEqual(
            robotstxt_rules(GOOGLE_ROBOTSTXT),
            # fmt: off
            [
                {'user_agent': '*', 'source': 2, 'rule_type': 'disallow', 'path': '/search'},
                {'user_agent': '*', 'source': 3, 'rule_type': 'allow', 'path': '/search/about'},
                {'user_agent': '*', 'source': 4, 'rule_type': 'allow', 'path': '/search/static'},
                {'user_agent': '*', 'source': 5, 'rule_type': 'allow', 'path': '/search/howsearchworks'},
                {'user_agent': '*', 'source': 6, 'rule_type': 'disallow', 'path': '/sdch'},
                {'user_agent': '*', 'source': 7, 'rule_type': 'disallow', 'path': '/groups'},
                {'user_agent': '*', 'source': 8, 'rule_type': 'disallow', 'path': '/index.html?'},
                {'user_agent': '*', 'source': 9, 'rule_type': 'disallow', 'path': '/?'},
                {'user_agent': '*', 'source': 10, 'rule_type': 'allow', 'path': '/?hl='},
                {'user_agent': '*', 'source': 11, 'rule_type': 'disallow', 'path': '/?hl=*&'},
                {'user_agent': '*', 'source': 12, 'rule_type': 'allow', 'path': '/?hl=*&gws_rd=ssl$'},
                {'user_agent': '*', 'source': 13, 'rule_type': 'disallow', 'path': '/?hl=*&*&gws_rd=ssl'},
                {'user_agent': '*', 'source': 14, 'rule_type': 'allow', 'path': '/?gws_rd=ssl$'},
                {'user_agent': '*', 'source': 15, 'rule_type': 'allow', 'path': '/?pt1=true$'},
                {'user_agent': '*', 'source': 16, 'rule_type': 'disallow', 'path': '/imgres'},
                {'user_agent': '*', 'source': 17, 'rule_type': 'disallow', 'path': '/u/'},
                {'user_agent': '*', 'source': 18, 'rule_type': 'disallow', 'path': '/preferences'},
                {'user_agent': '*', 'source': 19, 'rule_type': 'disallow', 'path': '/setprefs'},
                {'user_agent': '*', 'source': 20, 'rule_type': 'disallow', 'path': '/default'},
                {'user_agent': '*', 'source': 21, 'rule_type': 'disallow', 'path': '/m?'},
                {'user_agent': '*', 'source': 22, 'rule_type': 'disallow', 'path': '/m/'},
                {'user_agent': '*', 'source': 23, 'rule_type': 'allow', 'path': '/m/finance'},
                {'user_agent': '*', 'source': 24, 'rule_type': 'disallow', 'path': '/wml?'},
                {'user_agent': '*', 'source': 25, 'rule_type': 'disallow', 'path': '/wml/?'},
                {'user_agent': '*', 'source': 26, 'rule_type': 'disallow', 'path': '/wml/search?'},
                {'user_agent': '*', 'source': 27, 'rule_type': 'disallow', 'path': '/xhtml?'},
                {'user_agent': '*', 'source': 28, 'rule_type': 'disallow', 'path': '/xhtml/?'},
                {'user_agent': '*', 'source': 29, 'rule_type': 'disallow', 'path': '/xhtml/search?'},
                {'user_agent': '*', 'source': 30, 'rule_type': 'disallow', 'path': '/xml?'},
                {'user_agent': '*', 'source': 31, 'rule_type': 'disallow', 'path': '/imode?'},
                {'user_agent': '*', 'source': 32, 'rule_type': 'disallow', 'path': '/imode/?'},
                {'user_agent': '*', 'source': 33, 'rule_type': 'disallow', 'path': '/imode/search?'},
                {'user_agent': '*', 'source': 34, 'rule_type': 'disallow', 'path': '/jsky?'},
                {'user_agent': '*', 'source': 35, 'rule_type': 'disallow', 'path': '/jsky/?'},
                {'user_agent': '*', 'source': 36, 'rule_type': 'disallow', 'path': '/jsky/search?'},
                {'user_agent': '*', 'source': 37, 'rule_type': 'disallow', 'path': '/pda?'},
                {'user_agent': '*', 'source': 38, 'rule_type': 'disallow', 'path': '/pda/?'},
                {'user_agent': '*', 'source': 39, 'rule_type': 'disallow', 'path': '/pda/search?'},
                {'user_agent': '*', 'source': 40, 'rule_type': 'disallow', 'path': '/sprint_xhtml'},
                {'user_agent': '*', 'source': 41, 'rule_type': 'disallow', 'path': '/sprint_wml'},
                {'user_agent': '*', 'source': 42, 'rule_type': 'disallow', 'path': '/pqa'},
                {'user_agent': '*', 'source': 43, 'rule_type': 'disallow', 'path': '/palm'},
                {'user_agent': '*', 'source': 44, 'rule_type': 'disallow', 'path': '/gwt/'},
                {'user_agent': '*', 'source': 45, 'rule_type': 'disallow', 'path': '/purchases'},
                {'user_agent': '*', 'source': 46, 'rule_type': 'disallow', 'path': '/local?'},
                {'user_agent': '*', 'source': 47, 'rule_type': 'disallow', 'path': '/local_url'},
                {'user_agent': '*', 'source': 48, 'rule_type': 'disallow', 'path': '/shihui?'},
                {'user_agent': '*', 'source': 49, 'rule_type': 'disallow', 'path': '/shihui/'},
                {'user_agent': '*', 'source': 50, 'rule_type': 'disallow', 'path': '/products?'},
                {'user_agent': '*', 'source': 51, 'rule_type': 'disallow', 'path': '/product_'},
                {'user_agent': '*', 'source': 52, 'rule_type': 'disallow', 'path': '/products_'},
                {'user_agent': '*', 'source': 53, 'rule_type': 'disallow', 'path': '/products;'},
                {'user_agent': '*', 'source': 54, 'rule_type': 'disallow', 'path': '/print'},
                {'user_agent': '*', 'source': 55, 'rule_type': 'disallow', 'path': '/books/'},
                {'user_agent': '*', 'source': 56, 'rule_type': 'disallow', 'path': '/bkshp?*q=*'},
                {'user_agent': '*', 'source': 57, 'rule_type': 'disallow', 'path': '/books?*q=*'},
                {'user_agent': '*', 'source': 58, 'rule_type': 'disallow', 'path': '/books?*output=*'},
                {'user_agent': '*', 'source': 59, 'rule_type': 'disallow', 'path': '/books?*pg=*'},
                {'user_agent': '*', 'source': 60, 'rule_type': 'disallow', 'path': '/books?*jtp=*'},
                {'user_agent': '*', 'source': 61, 'rule_type': 'disallow', 'path': '/books?*jscmd=*'},
                {'user_agent': '*', 'source': 62, 'rule_type': 'disallow', 'path': '/books?*buy=*'},
                {'user_agent': '*', 'source': 63, 'rule_type': 'disallow', 'path': '/books?*zoom=*'},
                {'user_agent': '*', 'source': 64, 'rule_type': 'allow', 'path': '/books?*q=related:*'},
                {'user_agent': '*', 'source': 65, 'rule_type': 'allow', 'path': '/books?*q=editions:*'},
                {'user_agent': '*', 'source': 66, 'rule_type': 'allow', 'path': '/books?*q=subject:*'},
                {'user_agent': '*', 'source': 67, 'rule_type': 'allow', 'path': '/books/about'},
                {'user_agent': '*', 'source': 68, 'rule_type': 'allow', 'path': '/booksrightsholders'},
                {'user_agent': '*', 'source': 69, 'rule_type': 'allow', 'path': '/books?*zoom=1*'},
                {'user_agent': '*', 'source': 70, 'rule_type': 'allow', 'path': '/books?*zoom=5*'},
                {'user_agent': '*', 'source': 71, 'rule_type': 'allow', 'path': '/books/content?*zoom=1*'},
                {'user_agent': '*', 'source': 72, 'rule_type': 'allow', 'path': '/books/content?*zoom=5*'},
                {'user_agent': '*', 'source': 73, 'rule_type': 'disallow', 'path': '/ebooks/'},
                {'user_agent': '*', 'source': 74, 'rule_type': 'disallow', 'path': '/ebooks?*q=*'},
                {'user_agent': '*', 'source': 75, 'rule_type': 'disallow', 'path': '/ebooks?*output=*'},
                {'user_agent': '*', 'source': 76, 'rule_type': 'disallow', 'path': '/ebooks?*pg=*'},
                {'user_agent': '*', 'source': 77, 'rule_type': 'disallow', 'path': '/ebooks?*jscmd=*'},
                {'user_agent': '*', 'source': 78, 'rule_type': 'disallow', 'path': '/ebooks?*buy=*'},
                {'user_agent': '*', 'source': 79, 'rule_type': 'disallow', 'path': '/ebooks?*zoom=*'},
                {'user_agent': '*', 'source': 80, 'rule_type': 'allow', 'path': '/ebooks?*q=related:*'},
                {'user_agent': '*', 'source': 81, 'rule_type': 'allow', 'path': '/ebooks?*q=editions:*'},
                {'user_agent': '*', 'source': 82, 'rule_type': 'allow', 'path': '/ebooks?*q=subject:*'},
                {'user_agent': '*', 'source': 83, 'rule_type': 'allow', 'path': '/ebooks?*zoom=1*'},
                {'user_agent': '*', 'source': 84, 'rule_type': 'allow', 'path': '/ebooks?*zoom=5*'},
                {'user_agent': '*', 'source': 85, 'rule_type': 'disallow', 'path': '/patents?'},
                {'user_agent': '*', 'source': 86, 'rule_type': 'disallow', 'path': '/patents/download/'},
                {'user_agent': '*', 'source': 87, 'rule_type': 'disallow', 'path': '/patents/pdf/'},
                {'user_agent': '*', 'source': 88, 'rule_type': 'disallow', 'path': '/patents/related/'},
                {'user_agent': '*', 'source': 89, 'rule_type': 'disallow', 'path': '/scholar'},
                {'user_agent': '*', 'source': 90, 'rule_type': 'disallow', 'path': '/citations?'},
                {'user_agent': '*', 'source': 91, 'rule_type': 'allow', 'path': '/citations?user='},
                {'user_agent': '*', 'source': 92, 'rule_type': 'disallow', 'path': '/citations?*cstart='},
                {'user_agent': '*', 'source': 93, 'rule_type': 'allow', 'path': '/citations?view_op=new_profile'},
                {'user_agent': '*', 'source': 94, 'rule_type': 'allow', 'path': '/citations?view_op=top_venues'},
                {'user_agent': '*', 'source': 95, 'rule_type': 'allow', 'path': '/scholar_share'},
                {'user_agent': '*', 'source': 96, 'rule_type': 'disallow', 'path': '/s?'},
                {'user_agent': '*', 'source': 97, 'rule_type': 'disallow', 'path': '/maps?'},
                {'user_agent': '*', 'source': 98, 'rule_type': 'allow', 'path': '/maps?*output=classic*'},
                {'user_agent': '*', 'source': 99, 'rule_type': 'allow', 'path': '/maps?*file='},
                {'user_agent': '*', 'source': 100, 'rule_type': 'disallow', 'path': '/mapstt?'},
                {'user_agent': '*', 'source': 101, 'rule_type': 'disallow', 'path': '/mapslt?'},
                {'user_agent': '*', 'source': 102, 'rule_type': 'disallow', 'path': '/mapabcpoi?'},
                {'user_agent': '*', 'source': 103, 'rule_type': 'disallow', 'path': '/maphp?'},
                {'user_agent': '*', 'source': 104, 'rule_type': 'disallow', 'path': '/mapprint?'},
                {'user_agent': '*', 'source': 105, 'rule_type': 'disallow', 'path': '/maps/'},
                {'user_agent': '*', 'source': 106, 'rule_type': 'allow', 'path': '/maps/search/'},
                {'user_agent': '*', 'source': 107, 'rule_type': 'allow', 'path': '/maps/dir/'},
                {'user_agent': '*', 'source': 108, 'rule_type': 'allow', 'path': '/maps/d/'},
                {'user_agent': '*', 'source': 109, 'rule_type': 'allow', 'path': '/maps/reserve'},
                {'user_agent': '*', 'source': 110, 'rule_type': 'allow', 'path': '/maps/about'},
                {'user_agent': '*', 'source': 111, 'rule_type': 'allow', 'path': '/maps/match'},
                {'user_agent': '*', 'source': 112, 'rule_type': 'disallow', 'path': '/maps/api/js/'},
                {'user_agent': '*', 'source': 113, 'rule_type': 'allow', 'path': '/maps/api/js'},
                {'user_agent': '*', 'source': 114, 'rule_type': 'disallow', 'path': '/mld?'},
                {'user_agent': '*', 'source': 115, 'rule_type': 'disallow', 'path': '/staticmap?'},
                {'user_agent': '*', 'source': 116, 'rule_type': 'disallow', 'path': '/help/maps/streetview/partners/welcome/'},
                {'user_agent': '*', 'source': 117, 'rule_type': 'disallow', 'path': '/help/maps/indoormaps/partners/'},
                {'user_agent': '*', 'source': 118, 'rule_type': 'disallow', 'path': '/lochp?'},
                {'user_agent': '*', 'source': 119, 'rule_type': 'disallow', 'path': '/center'},
                {'user_agent': '*', 'source': 120, 'rule_type': 'disallow', 'path': '/ie?'},
                {'user_agent': '*', 'source': 121, 'rule_type': 'disallow', 'path': '/blogsearch/'},
                {'user_agent': '*', 'source': 122, 'rule_type': 'disallow', 'path': '/blogsearch_feeds'},
                {'user_agent': '*', 'source': 123, 'rule_type': 'disallow', 'path': '/advanced_blog_search'},
                {'user_agent': '*', 'source': 124, 'rule_type': 'disallow', 'path': '/uds/'},
                {'user_agent': '*', 'source': 125, 'rule_type': 'disallow', 'path': '/chart?'},
                {'user_agent': '*', 'source': 126, 'rule_type': 'disallow', 'path': '/transit?'},
                {'user_agent': '*', 'source': 127, 'rule_type': 'allow', 'path': '/calendar$'},
                {'user_agent': '*', 'source': 128, 'rule_type': 'allow', 'path': '/calendar/about/'},
                {'user_agent': '*', 'source': 129, 'rule_type': 'disallow', 'path': '/calendar/'},
                {'user_agent': '*', 'source': 130, 'rule_type': 'disallow', 'path': '/cl2/feeds/'},
                {'user_agent': '*', 'source': 131, 'rule_type': 'disallow', 'path': '/cl2/ical/'},
                {'user_agent': '*', 'source': 132, 'rule_type': 'disallow', 'path': '/coop/directory'},
                {'user_agent': '*', 'source': 133, 'rule_type': 'disallow', 'path': '/coop/manage'},
                {'user_agent': '*', 'source': 134, 'rule_type': 'disallow', 'path': '/trends?'},
                {'user_agent': '*', 'source': 135, 'rule_type': 'disallow', 'path': '/trends/music?'},
                {'user_agent': '*', 'source': 136, 'rule_type': 'disallow', 'path': '/trends/hottrends?'},
                {'user_agent': '*', 'source': 137, 'rule_type': 'disallow', 'path': '/trends/viz?'},
                {'user_agent': '*', 'source': 138, 'rule_type': 'disallow', 'path': '/trends/embed.js?'},
                {'user_agent': '*', 'source': 139, 'rule_type': 'disallow', 'path': '/trends/fetchComponent?'},
                {'user_agent': '*', 'source': 140, 'rule_type': 'disallow', 'path': '/trends/beta'},
                {'user_agent': '*', 'source': 141, 'rule_type': 'disallow', 'path': '/trends/topics'},
                {'user_agent': '*', 'source': 142, 'rule_type': 'disallow', 'path': '/musica'},
                {'user_agent': '*', 'source': 143, 'rule_type': 'disallow', 'path': '/musicad'},
                {'user_agent': '*', 'source': 144, 'rule_type': 'disallow', 'path': '/musicas'},
                {'user_agent': '*', 'source': 145, 'rule_type': 'disallow', 'path': '/musicl'},
                {'user_agent': '*', 'source': 146, 'rule_type': 'disallow', 'path': '/musics'},
                {'user_agent': '*', 'source': 147, 'rule_type': 'disallow', 'path': '/musicsearch'},
                {'user_agent': '*', 'source': 148, 'rule_type': 'disallow', 'path': '/musicsp'},
                {'user_agent': '*', 'source': 149, 'rule_type': 'disallow', 'path': '/musiclp'},
                {'user_agent': '*', 'source': 150, 'rule_type': 'disallow', 'path': '/urchin_test/'},
                {'user_agent': '*', 'source': 151, 'rule_type': 'disallow', 'path': '/movies?'},
                {'user_agent': '*', 'source': 152, 'rule_type': 'disallow', 'path': '/wapsearch?'},
                {'user_agent': '*', 'source': 153, 'rule_type': 'allow', 'path': '/safebrowsing/diagnostic'},
                {'user_agent': '*', 'source': 154, 'rule_type': 'allow', 'path': '/safebrowsing/report_badware/'},
                {'user_agent': '*', 'source': 155, 'rule_type': 'allow', 'path': '/safebrowsing/report_error/'},
                {'user_agent': '*', 'source': 156, 'rule_type': 'allow', 'path': '/safebrowsing/report_phish/'},
                {'user_agent': '*', 'source': 157, 'rule_type': 'disallow', 'path': '/reviews/search?'},
                {'user_agent': '*', 'source': 158, 'rule_type': 'disallow', 'path': '/orkut/albums'},
                {'user_agent': '*', 'source': 159, 'rule_type': 'disallow', 'path': '/cbk'},
                {'user_agent': '*', 'source': 160, 'rule_type': 'disallow', 'path': '/recharge/dashboard/car'},
                {'user_agent': '*', 'source': 161, 'rule_type': 'disallow', 'path': '/recharge/dashboard/static/'},
                {'user_agent': '*', 'source': 162, 'rule_type': 'disallow', 'path': '/profiles/me'},
                {'user_agent': '*', 'source': 163, 'rule_type': 'allow', 'path': '/profiles'},
                {'user_agent': '*', 'source': 164, 'rule_type': 'disallow', 'path': '/s2/profiles/me'},
                {'user_agent': '*', 'source': 165, 'rule_type': 'allow', 'path': '/s2/profiles'},
                {'user_agent': '*', 'source': 166, 'rule_type': 'allow', 'path': '/s2/oz'},
                {'user_agent': '*', 'source': 167, 'rule_type': 'allow', 'path': '/s2/photos'},
                {'user_agent': '*', 'source': 168, 'rule_type': 'allow', 'path': '/s2/search/social'},
                {'user_agent': '*', 'source': 169, 'rule_type': 'allow', 'path': '/s2/static'},
                {'user_agent': '*', 'source': 170, 'rule_type': 'disallow', 'path': '/s2'},
                {'user_agent': '*', 'source': 171, 'rule_type': 'disallow', 'path': '/transconsole/portal/'},
                {'user_agent': '*', 'source': 172, 'rule_type': 'disallow', 'path': '/gcc/'},
                {'user_agent': '*', 'source': 173, 'rule_type': 'disallow', 'path': '/aclk'},
                {'user_agent': '*', 'source': 174, 'rule_type': 'disallow', 'path': '/cse?'},
                {'user_agent': '*', 'source': 175, 'rule_type': 'disallow', 'path': '/cse/home'},
                {'user_agent': '*', 'source': 176, 'rule_type': 'disallow', 'path': '/cse/panel'},
                {'user_agent': '*', 'source': 177, 'rule_type': 'disallow', 'path': '/cse/manage'},
                {'user_agent': '*', 'source': 178, 'rule_type': 'disallow', 'path': '/tbproxy/'},
                {'user_agent': '*', 'source': 179, 'rule_type': 'disallow', 'path': '/imesync/'},
                {'user_agent': '*', 'source': 180, 'rule_type': 'disallow', 'path': '/shenghuo/search?'},
                {'user_agent': '*', 'source': 181, 'rule_type': 'disallow', 'path': '/support/forum/search?'},
                {'user_agent': '*', 'source': 182, 'rule_type': 'disallow', 'path': '/reviews/polls/'},
                {'user_agent': '*', 'source': 183, 'rule_type': 'disallow', 'path': '/hosted/images/'},
                {'user_agent': '*', 'source': 184, 'rule_type': 'disallow', 'path': '/ppob/?'},
                {'user_agent': '*', 'source': 185, 'rule_type': 'disallow', 'path': '/ppob?'},
                {'user_agent': '*', 'source': 186, 'rule_type': 'disallow', 'path': '/accounts/ClientLogin'},
                {'user_agent': '*', 'source': 187, 'rule_type': 'disallow', 'path': '/accounts/ClientAuth'},
                {'user_agent': '*', 'source': 188, 'rule_type': 'disallow', 'path': '/accounts/o8'},
                {'user_agent': '*', 'source': 189, 'rule_type': 'allow', 'path': '/accounts/o8/id'},
                {'user_agent': '*', 'source': 190, 'rule_type': 'disallow', 'path': '/topicsearch?q='},
                {'user_agent': '*', 'source': 191, 'rule_type': 'disallow', 'path': '/xfx7/'},
                {'user_agent': '*', 'source': 192, 'rule_type': 'disallow', 'path': '/squared/api'},
                {'user_agent': '*', 'source': 193, 'rule_type': 'disallow', 'path': '/squared/search'},
                {'user_agent': '*', 'source': 194, 'rule_type': 'disallow', 'path': '/squared/table'},
                {'user_agent': '*', 'source': 195, 'rule_type': 'disallow', 'path': '/qnasearch?'},
                {'user_agent': '*', 'source': 196, 'rule_type': 'disallow', 'path': '/app/updates'},
                {'user_agent': '*', 'source': 197, 'rule_type': 'disallow', 'path': '/sidewiki/entry/'},
                {'user_agent': '*', 'source': 198, 'rule_type': 'disallow', 'path': '/quality_form?'},
                {'user_agent': '*', 'source': 199, 'rule_type': 'disallow', 'path': '/labs/popgadget/search'},
                {'user_agent': '*', 'source': 200, 'rule_type': 'disallow', 'path': '/buzz/post'},
                {'user_agent': '*', 'source': 201, 'rule_type': 'disallow', 'path': '/compressiontest/'},
                {'user_agent': '*', 'source': 202, 'rule_type': 'disallow', 'path': '/analytics/feeds/'},
                {'user_agent': '*', 'source': 203, 'rule_type': 'disallow', 'path': '/analytics/partners/comments/'},
                {'user_agent': '*', 'source': 204, 'rule_type': 'disallow', 'path': '/analytics/portal/'},
                {'user_agent': '*', 'source': 205, 'rule_type': 'disallow', 'path': '/analytics/uploads/'},
                {'user_agent': '*', 'source': 206, 'rule_type': 'allow', 'path': '/alerts/manage'},
                {'user_agent': '*', 'source': 207, 'rule_type': 'allow', 'path': '/alerts/remove'},
                {'user_agent': '*', 'source': 208, 'rule_type': 'disallow', 'path': '/alerts/'},
                {'user_agent': '*', 'source': 209, 'rule_type': 'allow', 'path': '/alerts/$'},
                {'user_agent': '*', 'source': 210, 'rule_type': 'disallow', 'path': '/ads/search?'},
                {'user_agent': '*', 'source': 211, 'rule_type': 'disallow', 'path': '/ads/plan/action_plan?'},
                {'user_agent': '*', 'source': 212, 'rule_type': 'disallow', 'path': '/ads/plan/api/'},
                {'user_agent': '*', 'source': 213, 'rule_type': 'disallow', 'path': '/ads/hotels/partners'},
                {'user_agent': '*', 'source': 214, 'rule_type': 'disallow', 'path': '/phone/compare/?'},
                {'user_agent': '*', 'source': 215, 'rule_type': 'disallow', 'path': '/travel/clk'},
                {'user_agent': '*', 'source': 216, 'rule_type': 'disallow', 'path': '/travel/flights/s/'},
                {'user_agent': '*', 'source': 217, 'rule_type': 'disallow', 'path': '/hotelfinder/rpc'},
                {'user_agent': '*', 'source': 218, 'rule_type': 'disallow', 'path': '/hotels/rpc'},
                {'user_agent': '*', 'source': 219, 'rule_type': 'disallow', 'path': '/commercesearch/services/'},
                {'user_agent': '*', 'source': 220, 'rule_type': 'disallow', 'path': '/evaluation/'},
                {'user_agent': '*', 'source': 221, 'rule_type': 'disallow', 'path': '/chrome/browser/mobile/tour'},
                {'user_agent': '*', 'source': 222, 'rule_type': 'disallow', 'path': '/compare/*/apply*'},
                {'user_agent': '*', 'source': 223, 'rule_type': 'disallow', 'path': '/forms/perks/'},
                {'user_agent': '*', 'source': 224, 'rule_type': 'disallow', 'path': '/shopping/suppliers/search'},
                {'user_agent': '*', 'source': 225, 'rule_type': 'disallow', 'path': '/ct/'},
                {'user_agent': '*', 'source': 226, 'rule_type': 'disallow', 'path': '/edu/cs4hs/'},
                {'user_agent': '*', 'source': 227, 'rule_type': 'disallow', 'path': '/trustedstores/s/'},
                {'user_agent': '*', 'source': 228, 'rule_type': 'disallow', 'path': '/trustedstores/tm2'},
                {'user_agent': '*', 'source': 229, 'rule_type': 'disallow', 'path': '/trustedstores/verify'},
                {'user_agent': '*', 'source': 230, 'rule_type': 'disallow', 'path': '/adwords/proposal'},
                {'user_agent': '*', 'source': 231, 'rule_type': 'disallow', 'path': '/shopping?*'},
                {'user_agent': '*', 'source': 232, 'rule_type': 'disallow', 'path': '/shopping/product/'},
                {'user_agent': '*', 'source': 233, 'rule_type': 'disallow', 'path': '/shopping/seller'},
                {'user_agent': '*', 'source': 234, 'rule_type': 'disallow', 'path': '/shopping/ratings/account/metrics'},
                {'user_agent': '*', 'source': 235, 'rule_type': 'disallow', 'path': '/shopping/ratings/merchant/immersivedetails'},
                {'user_agent': '*', 'source': 236, 'rule_type': 'disallow', 'path': '/shopping/reviewer'},
                {'user_agent': '*', 'source': 237, 'rule_type': 'disallow', 'path': '/about/careers/applications/'},
                {'user_agent': '*', 'source': 238, 'rule_type': 'disallow', 'path': '/about/careers/applications-a/'},
                {'user_agent': '*', 'source': 239, 'rule_type': 'disallow', 'path': '/landing/signout.html'},
                {'user_agent': '*', 'source': 240, 'rule_type': 'disallow', 'path': '/webmasters/sitemaps/ping?'},
                {'user_agent': '*', 'source': 241, 'rule_type': 'disallow', 'path': '/ping?'},
                {'user_agent': '*', 'source': 242, 'rule_type': 'disallow', 'path': '/gallery/'},
                {'user_agent': '*', 'source': 243, 'rule_type': 'disallow', 'path': '/landing/now/ontap/'},
                {'user_agent': '*', 'source': 244, 'rule_type': 'allow', 'path': '/searchhistory/'},
                {'user_agent': '*', 'source': 245, 'rule_type': 'allow', 'path': '/maps/reserve'},
                {'user_agent': '*', 'source': 246, 'rule_type': 'allow', 'path': '/maps/reserve/partners'},
                {'user_agent': '*', 'source': 247, 'rule_type': 'disallow', 'path': '/maps/reserve/api/'},
                {'user_agent': '*', 'source': 248, 'rule_type': 'disallow', 'path': '/maps/reserve/search'},
                {'user_agent': '*', 'source': 249, 'rule_type': 'disallow', 'path': '/maps/reserve/bookings'},
                {'user_agent': '*', 'source': 250, 'rule_type': 'disallow', 'path': '/maps/reserve/settings'},
                {'user_agent': '*', 'source': 251, 'rule_type': 'disallow', 'path': '/maps/reserve/manage'},
                {'user_agent': '*', 'source': 252, 'rule_type': 'disallow', 'path': '/maps/reserve/payment'},
                {'user_agent': '*', 'source': 253, 'rule_type': 'disallow', 'path': '/maps/reserve/receipt'},
                {'user_agent': '*', 'source': 254, 'rule_type': 'disallow', 'path': '/maps/reserve/sellersignup'},
                {'user_agent': '*', 'source': 255, 'rule_type': 'disallow', 'path': '/maps/reserve/payments'},
                {'user_agent': '*', 'source': 256, 'rule_type': 'disallow', 'path': '/maps/reserve/feedback'},
                {'user_agent': '*', 'source': 257, 'rule_type': 'disallow', 'path': '/maps/reserve/terms'},
                {'user_agent': '*', 'source': 258, 'rule_type': 'disallow', 'path': '/maps/reserve/m/'},
                {'user_agent': '*', 'source': 259, 'rule_type': 'disallow', 'path': '/maps/reserve/b/'},
                {'user_agent': '*', 'source': 260, 'rule_type': 'disallow', 'path': '/maps/reserve/partner-dashboard'},
                {'user_agent': '*', 'source': 261, 'rule_type': 'disallow', 'path': '/about/views/'},
                {'user_agent': '*', 'source': 262, 'rule_type': 'disallow', 'path': '/intl/*/about/views/'},
                {'user_agent': '*', 'source': 263, 'rule_type': 'disallow', 'path': '/local/cars'},
                {'user_agent': '*', 'source': 264, 'rule_type': 'disallow', 'path': '/local/cars/'},
                {'user_agent': '*', 'source': 265, 'rule_type': 'disallow', 'path': '/local/dealership/'},
                {'user_agent': '*', 'source': 266, 'rule_type': 'disallow', 'path': '/local/dining/'},
                {'user_agent': '*', 'source': 267, 'rule_type': 'disallow', 'path': '/local/place/products/'},
                {'user_agent': '*', 'source': 268, 'rule_type': 'disallow', 'path': '/local/place/reviews/'},
                {'user_agent': '*', 'source': 269, 'rule_type': 'disallow', 'path': '/local/place/rap/'},
                {'user_agent': '*', 'source': 270, 'rule_type': 'disallow', 'path': '/local/tab/'},
                {'user_agent': '*', 'source': 271, 'rule_type': 'disallow', 'path': '/localservices/*'},
                {'user_agent': '*', 'source': 272, 'rule_type': 'allow', 'path': '/finance'},
                {'user_agent': '*', 'source': 273, 'rule_type': 'allow', 'path': '/js/'},
                {'user_agent': '*', 'source': 274, 'rule_type': 'disallow', 'path': '/nonprofits/account/'},
                {'user_agent': '*', 'source': 275, 'rule_type': 'disallow', 'path': '/fbx'},
                {'user_agent': '*', 'source': 276, 'rule_type': 'disallow', 'path': '/uviewer'},
                {'user_agent': '*', 'source': 277, 'rule_type': 'disallow', 'path': '/landing/cmsnext-root/'},
                {'user_agent': 'AdsBot-Google', 'source': 281, 'rule_type': 'disallow', 'path': '/maps/api/js/'},
                {'user_agent': 'AdsBot-Google', 'source': 282, 'rule_type': 'allow', 'path': '/maps/api/js'},
                {'user_agent': 'AdsBot-Google', 'source': 283, 'rule_type': 'disallow', 'path': '/maps/api/place/js/'},
                {'user_agent': 'AdsBot-Google', 'source': 284, 'rule_type': 'disallow', 'path': '/maps/api/staticmap'},
                {'user_agent': 'AdsBot-Google', 'source': 285, 'rule_type': 'disallow', 'path': '/maps/api/streetview'},
                {'user_agent': 'Twitterbot', 'source': 289, 'rule_type': 'allow', 'path': '/imgres'},
                {'user_agent': 'Twitterbot', 'source': 290, 'rule_type': 'allow', 'path': '/search'},
                {'user_agent': 'Twitterbot', 'source': 291, 'rule_type': 'disallow', 'path': '/groups'},
                {'user_agent': 'Twitterbot', 'source': 292, 'rule_type': 'disallow', 'path': '/hosted/images/'},
                {'user_agent': 'Twitterbot', 'source': 293, 'rule_type': 'disallow', 'path': '/m/'},
                {'user_agent': 'facebookexternalhit', 'source': 296, 'rule_type': 'allow', 'path': '/imgres'},
                {'user_agent': 'facebookexternalhit', 'source': 297, 'rule_type': 'allow', 'path': '/search'},
                {'user_agent': 'facebookexternalhit', 'source': 298, 'rule_type': 'disallow', 'path': '/groups'},
                {'user_agent': 'facebookexternalhit', 'source': 299, 'rule_type': 'disallow', 'path': '/hosted/images/'},
                {'user_agent': 'facebookexternalhit', 'source': 300, 'rule_type': 'disallow', 'path': '/m/'}
            ]
        )

        self.assertEqual(
            robotstxt_rules('''
User-agent: *

User-agent: grapeshot
Disallow:

Allow: /editorial/wp-admin/admin-ajax.php
'''),
[{'path': '', 'rule_type': 'disallow', 'source': 5, 'user_agent': 'grapeshot'},
  {'path': '/editorial/wp-admin/admin-ajax.php',
   'rule_type': 'allow',
   'source': 7,
   'user_agent': 'grapeshot'}]
        )


class TestCoverage(unittest.TestCase):
    def test_coverage(self):
        test_methods = [
            method for method in dir(TestRobotstxt) if method.startswith("test_")
        ]
        funcs_with_tests = set([x.replace("test_", "") for x in test_methods])

        for func in FUNCTIONS:
            self.assertTrue(
                func in funcs_with_tests,
                f"{func} does not have corresponding test in {funcs_with_tests}",
            )

        for module in MODULES:
            self.assertTrue(
                module in funcs_with_tests,
                f"{module} does not have corresponding test in {funcs_with_tests}",
            )


if __name__ == "__main__":
    unittest.main()
