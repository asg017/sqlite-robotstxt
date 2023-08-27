#[cfg(feature = "robotstxt")]
#[link(name = "sqlite_robotstxt0")]
extern "C" {
    pub fn sqlite3_robotstxt_init();
}

#[cfg(feature = "hola")]
#[link(name = "sqlite_hola0")]
extern "C" {
    pub fn sqlite3_hola_init();
}

#[cfg(test)]
mod tests {
    use super::*;

    use rusqlite::{ffi::sqlite3_auto_extension, Connection};

    #[test]
    fn test_rusqlite_auto_extension() {
        unsafe {
            sqlite3_auto_extension(Some(sqlite3_robotstxt_init));
            sqlite3_auto_extension(Some(sqlite3_hola_init));
        }

        let conn = Connection::open_in_memory().unwrap();

        let result: String = conn
            .query_row("select robotstxt(?)", ["alex"], |x| x.get(0))
            .unwrap();

        assert_eq!(result, "robotstxt, alex!");

        let result: String = conn
            .query_row("select hola(?)", ["alex"], |x| x.get(0))
            .unwrap();

        assert_eq!(result, "¡Hola, alex!");
    }
}
