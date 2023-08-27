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

Find all User-Agents listed in a `robots.txt` file.

```sql
select *
from robotstxt_user_agents(
  readfile('robots.txt')
);
/*
┌─────────────────────┬────────┬───────┐
│        name         │ source │ rules │
├─────────────────────┼────────┼───────┤
│ *                   │ 1      │       │
│ AdsBot-Google       │ 280    │       │
│ Twitterbot          │ 288    │       │
│ facebookexternalhit │ 295    │       │
└─────────────────────┴────────┴───────┘
*/
```

Use with `sqlite-http` to requests `robots.txt` files on the fly.

```sql
select *
from robotstxt_user_agents(
  http_get_body('https://en.wikipedia.org/robots.txt')
)
limit 10;
/*
┌────────────────────────────┬────────┬───────┐
│            name            │ source │ rules │
├────────────────────────────┼────────┼───────┤
│ MJ12bot                    │ 11     │       │
│ Mediapartners-Google*      │ 15     │       │
│ IsraBot                    │ 19     │       │
│ Orthogaffe                 │ 22     │       │
│ UbiCrawler                 │ 27     │       │
│ DOC                        │ 30     │       │
│ Zao                        │ 33     │       │
│ sitecheck.internetseer.com │ 38     │       │
│ Zealbot                    │ 41     │       │
│ MSIECrawler                │ 44     │       │
└────────────────────────────┴────────┴───────┘
*/
```

## TODO

- [ ] `robotstxt_allowed(rules, path)` overload on `robotstxt_user_agents`
- [ ] `robotstxt_rules`
- [ ] sitemaps?
- [ ] unknown directives?
