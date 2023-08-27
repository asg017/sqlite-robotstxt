import { download } from "https://deno.land/x/plug@1.0.1/mod.ts";
import meta from "./deno.json" assert { type: "json" };

const BASE = `${meta.github}/releases/download/v${meta.version}`;

// Similar to https://github.com/denodrivers/sqlite3/blob/f7529897720631c2341b713f0d78d4d668593ea9/src/ffi.ts#L561
let path: string;
try {
  const customPath = Deno.env.get("DENO_SQLITE_robotstxt_PATH");
  if (customPath) path = customPath;
  else {
    path = await download({
      url: {
        darwin: {
          aarch64: `${BASE}/sqlite-lines-v${meta.version}-deno-darwin-aarch64.robotstxt0.dylib`,
          x86_64: `${BASE}/sqlite-lines-v${meta.version}-deno-darwin-x86_64.robotstxt0.dylib`,
        },
        windows: {
          x86_64: `${BASE}/sqlite-lines-v${meta.version}-deno-windows-x86_64.robotstxt0.dll`,
        },
        linux: {
          x86_64: `${BASE}/sqlite-lines-v${meta.version}-deno-linux-x86_64.robotstxt0.so`,
        },
      },
      suffixes: {
        darwin: "",
        linux: "",
        windows: "",
      },
    });
  }
} catch (e) {
  if (e instanceof Deno.errors.PermissionDenied) {
    throw e;
  }

  const error = new Error("Failed to load sqlite-robotstxt extension");
  error.cause = e;

  throw error;
}

/**
 * Returns the full path to the compiled sqlite-robotstxt extension.
 * Caution: this will not be named "robotstxt0.dylib|so|dll", since plug will
 * replace the name with a hash.
 */
export function getLoadablePath(): string {
  return path;
}

/**
 * Entrypoint name for the sqlite-robotstxt extension.
 */
export const entrypoint = "sqlite3_robotstxt_init";

interface Db {
  // after https://deno.land/x/sqlite3@0.8.0/mod.ts?s=Database#method_loadExtension_0
  loadExtension(file: string, entrypoint?: string | undefined): void;
}
/**
 * Loads the sqlite-robotstxt extension on the given sqlite3 database.
 */
export function load(db: Db): void {
  db.loadExtension(path, entrypoint);
}
