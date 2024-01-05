# sqlite-robotstxt

A SQLite extension for parsing [`robots.txt`](https://en.wikipedia.org/wiki/Robots.txt) files. Based on [`sqlite-loadable-rs`](https://github.com/asg017/sqlite-loadable-rs) and the [`robotstxt` crate](https://docs.rs/robotstxt/latest/robotstxt/).

## Usage

See if a specified User-Agent can access a specific path, based on the rules of a `robots.txt`.

```sql
select robotstxt_matches(
  readfile('robots.txt'),
  'My-Agent',
  '/path'
); -- 0 or 1
```

Find all indvidual rules specified in a `robots.txt` file.

```sql
select *
from robotstxt_rules(
  readfile('tests/examples/en.wikipedia.org.robots.txt')
)
limit 10;
/*
┌────────────────────────────┬────────┬───────────┬──────┐
│         user_agent         │ source │ rule_type │ path │
├────────────────────────────┼────────┼───────────┼──────┤
│ MJ12bot                    │ 12     │ disallow  │ /    │
│ Mediapartners-Google*      │ 16     │ disallow  │ /    │
│ IsraBot                    │ 20     │ disallow  │      │
│ Orthogaffe                 │ 23     │ disallow  │      │
│ UbiCrawler                 │ 28     │ disallow  │ /    │
│ DOC                        │ 31     │ disallow  │ /    │
│ Zao                        │ 34     │ disallow  │ /    │
│ sitecheck.internetseer.com │ 39     │ disallow  │ /    │
│ Zealbot                    │ 42     │ disallow  │ /    │
│ MSIECrawler                │ 45     │ disallow  │ /    │
└────────────────────────────┴────────┴───────────┴──────┘
*/
```

Use with `sqlite-http` to requests `robots.txt` files on the fly.

```sql
select *
from robotstxt_rules(
  http_get_body('https://www.reddit.com/robots.txt')
)
limit 10;


/*
┌────────────┬────────┬───────────┬─────────────────────┐
│ user_agent │ source │ rule_type │        path         │
├────────────┼────────┼───────────┼─────────────────────┤
│ 008        │ 3      │ disallow  │ /                   │
│ voltron    │ 7      │ disallow  │ /                   │
│ bender     │ 10     │ disallow  │ /my_shiny_metal_ass │
│ Gort       │ 13     │ disallow  │ /earth              │
│ MJ12bot    │ 16     │ disallow  │ /                   │
│ PiplBot    │ 19     │ disallow  │ /                   │
│ *          │ 22     │ disallow  │ /*.json             │
│ *          │ 23     │ disallow  │ /*.json-compact     │
│ *          │ 24     │ disallow  │ /*.json-html        │
│ *          │ 25     │ disallow  │ /*.xml              │
└────────────┴────────┴───────────┴─────────────────────┘
*/
```

## TODO

- [ ] `robotstxt_allowed(rules, path)` overload on `robotstxt_user_agents`
- [ ] sitemaps?
- [ ] unknown directives?

- [ ] pytest + syrupy
- [ ] ensure no panics
