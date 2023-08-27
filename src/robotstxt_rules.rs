//! cargo build --example series
//! sqlite3 :memory: '.read examples/test.sql'

use sqlite_loadable::prelude::*;
use sqlite_loadable::{
    api, define_table_function,
    table::{BestIndexError, ConstraintOperator, IndexInfo, VTab, VTabArguments, VTabCursor},
    Result,
};

use crate::utils::{parse, RobotsInfo};
use std::{mem, os::raw::c_int};
static CREATE_SQL: &str =
    "CREATE TABLE x(user_agent text, source int, rule_type text, path text, robotstxt hidden)";
enum Columns {
    UserAgent,
    Source,
    RuleType,
    Path,
    Robotstxt,
}
fn column(index: i32) -> Option<Columns> {
    match index {
        0 => Some(Columns::UserAgent),
        1 => Some(Columns::Source),
        2 => Some(Columns::RuleType),
        3 => Some(Columns::Path),
        4 => Some(Columns::Robotstxt),
        _ => None,
    }
}

#[repr(C)]
pub struct UserAgentsTable {
    base: sqlite3_vtab,
}

impl<'vtab> VTab<'vtab> for UserAgentsTable {
    type Aux = ();
    type Cursor = UserAgentsCursor;

    fn connect(
        _db: *mut sqlite3,
        _aux: Option<&Self::Aux>,
        _args: VTabArguments,
    ) -> Result<(String, UserAgentsTable)> {
        let base: sqlite3_vtab = unsafe { mem::zeroed() };
        let vtab = UserAgentsTable { base };
        // TODO db.config(VTabConfig::Innocuous)?;
        Ok((CREATE_SQL.to_owned(), vtab))
    }
    fn destroy(&self) -> Result<()> {
        Ok(())
    }

    fn best_index(&self, mut info: IndexInfo) -> core::result::Result<(), BestIndexError> {
        let mut has_robotstxt = false;
        for mut constraint in info.constraints() {
            match column(constraint.column_idx()) {
                Some(Columns::Robotstxt) => {
                    if constraint.usable() && constraint.op() == Some(ConstraintOperator::EQ) {
                        constraint.set_omit(true);
                        constraint.set_argv_index(1);
                        has_robotstxt = true;
                    } else {
                        return Err(BestIndexError::Constraint);
                    }
                }
                _ => todo!(),
            }
        }
        if !has_robotstxt {
            return Err(BestIndexError::Error);
        }
        info.set_estimated_cost(100000.0);
        info.set_estimated_rows(100000);
        info.set_idxnum(1);

        Ok(())
    }

    fn open(&mut self) -> Result<UserAgentsCursor> {
        Ok(UserAgentsCursor::new())
    }
}

#[repr(C)]
pub struct UserAgentsCursor {
    /// Base class. Must be first
    base: sqlite3_vtab_cursor,
    rowid: i64,
    useragent_rowid: i64,
    rule_rowid: i64,
    info: Option<RobotsInfo>,
}
impl UserAgentsCursor {
    fn new() -> UserAgentsCursor {
        let base: sqlite3_vtab_cursor = unsafe { mem::zeroed() };
        UserAgentsCursor {
            base,
            rowid: 0,
            useragent_rowid: 0,
            rule_rowid: 0,
            info: None,
        }
    }
}

impl VTabCursor for UserAgentsCursor {
    fn filter(
        &mut self,
        _idx_num: c_int,
        _idx_str: Option<&str>,
        values: &[*mut sqlite3_value],
    ) -> Result<()> {
        let robotstxt = api::value_text(values.get(0).unwrap()).unwrap();
        self.info = Some(parse(robotstxt));
        self.rowid = 0;
        self.useragent_rowid = 0;
        self.rule_rowid = 0;
        Ok(())
    }

    fn next(&mut self) -> Result<()> {
        self.rowid += 1;
        let user_agent = self.info.unwrap().user_agents.get(self.useragent_rowid);

        Ok(())
    }

    fn eof(&self) -> bool {
        (self.rowid as usize) >= self.info.as_ref().unwrap().user_agents.len()
    }

    fn column(&self, context: *mut sqlite3_context, i: c_int) -> Result<()> {
        let user_agents = &self.info.as_ref().unwrap().user_agents;
        let current = user_agents.get(self.rowid as usize).unwrap();
        match column(i) {
            //Some(Columns::Name) => api::result_text(context, current.name.clone())?,
            Some(Columns::Source) => api::result_int64(context, current.line_number.into()),
            _ => (),
        }
        Ok(())
    }

    fn rowid(&self) -> Result<i64> {
        Ok(self.rowid)
    }
}
