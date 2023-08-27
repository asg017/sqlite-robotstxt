const fs = require("fs").promises;

module.exports = async ({ github, context }) => {
  const {
    repo: { owner, repo },
    sha,
  } = context;
  console.log(process.env.GITHUB_REF);
  const release = await github.rest.repos.getReleaseByTag({
    owner,
    repo,
    tag: process.env.GITHUB_REF.replace("refs/tags/", ""),
  });
  console.log("release id: ", release.data.id);
  const release_id = release.data.id;

  const compiled_extensions = [
    {
      path: "sqlite-robotstxt-macos-arm/robotstxt0.dylib",
      name: "deno-darwin-aarch64.robotstxt0.dylib",
    },
    {
      path: "sqlite-robotstxt-macos/robotstxt0.dylib",
      name: "deno-darwin-x86_64.robotstxt0.dylib",
    },
    {
      path: "sqlite-robotstxt-ubuntu/robotstxt0.so",
      name: "deno-linux-x86_64.robotstxt0.so",
    },
    {
      path: "sqlite-robotstxt-windows/robotstxt0.dll",
      name: "deno-windows-x86_64.robotstxt0.dll",
    },
  ];
  await Promise.all(
    compiled_extensions.map(async ({ name, path }) => {
      return github.rest.repos.uploadReleaseAsset({
        owner,
        repo,
        release_id,
        name,
        data: await fs.readFile(path),
      });
    })
  );
};
