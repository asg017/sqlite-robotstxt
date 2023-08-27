# The `datasette-sqlite-robotstxt` Datasette Plugin

`datasette-sqlite-robotstxt` is a [Datasette plugin](https://docs.datasette.io/en/stable/plugins.html) that loads the [`sqlite-robotstxt`](https://github.com/asg017/sqlite-robotstxt) extension in Datasette instances.

```
datasette install datasette-sqlite-robotstxt
```

See [`docs.md`](../../docs.md) for a full API reference for the robotstxt SQL functions.

Alternatively, when publishing Datasette instances, you can use the `--install` option to install the plugin.

```
datasette publish cloudrun data.db --service=my-service --install=datasette-sqlite-robotstxt

```
