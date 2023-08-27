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
