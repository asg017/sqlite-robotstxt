//! cargo build --example series
//! sqlite3 :memory: '.read examples/test.sql'

use sqlite_loadable::prelude::*;
use sqlite_loadable::{
    api,
    table::{BestIndexError, ConstraintOperator, IndexInfo, VTab, VTabArguments, VTabCursor},
    Error, Result,
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
pub struct RulesTable {
    base: sqlite3_vtab,
}

impl<'vtab> VTab<'vtab> for RulesTable {
    type Aux = ();
    type Cursor = RulesCursor;

    fn connect(
        _db: *mut sqlite3,
        _aux: Option<&Self::Aux>,
        _args: VTabArguments,
    ) -> Result<(String, RulesTable)> {
        let base: sqlite3_vtab = unsafe { mem::zeroed() };
        let vtab = RulesTable { base };
        // TODO db.config(VTabConfig::Innocuous)?;
        Ok((CREATE_SQL.to_owned(), vtab))
    }
    fn destroy(&self) -> Result<()> {
        Ok(())
    }

    fn best_index(&self, mut info: IndexInfo) -> core::result::Result<(), BestIndexError> {
        let mut has_robotstxt = false;
        for mut constraint in info.constraints() {
            if let Some(Columns::Robotstxt) = column(constraint.column_idx()) {
                if constraint.usable() && constraint.op() == Some(ConstraintOperator::EQ) {
                    constraint.set_omit(true);
                    constraint.set_argv_index(1);
                    has_robotstxt = true;
                } else {
                    return Err(BestIndexError::Constraint);
                }
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

    fn open(&mut self) -> Result<RulesCursor> {
        Ok(RulesCursor::new())
    }
}

#[repr(C)]
pub struct RulesCursor {
    /// Base class. Must be first
    base: sqlite3_vtab_cursor,
    rowid: i64,
    useragent_rowid: usize,
    rule_rowid: usize,
    info: Option<RobotsInfo>,
}
impl RulesCursor {
    fn new() -> RulesCursor {
        let base: sqlite3_vtab_cursor = unsafe { mem::zeroed() };
        RulesCursor {
            base,
            rowid: 0,
            useragent_rowid: 0,
            rule_rowid: 0,
            info: None,
        }
    }
}

impl VTabCursor for RulesCursor {
    fn filter(
        &mut self,
        _idx_num: c_int,
        _idx_str: Option<&str>,
        values: &[*mut sqlite3_value],
    ) -> Result<()> {
        let robotstxt = api::value_text(values.get(0).ok_or_else(|| Error::new_message("TODO"))?)
            .map_err(|_| Error::new_message("TODO"))?;
        let info = parse(robotstxt);
        self.rowid = 0;
        self.useragent_rowid = 0;
        self.rule_rowid = 0;
        while let Some(user_agent) = info.user_agents.get(self.useragent_rowid) {
            if user_agent.rules.get(self.rule_rowid).is_none() {
                self.useragent_rowid += 1;
            } else {
                break;
            }
        }
        self.info = Some(info);
        Ok(())
    }

    fn next(&mut self) -> Result<()> {
        self.rowid += 1;
        let info = self.info.as_ref().unwrap();
        let user_agent = info.user_agents.get(self.useragent_rowid);
        let user_agent = match user_agent {
            None => return Ok(()),
            Some(user_agent) => user_agent,
        };
        match user_agent.rules.get(self.rule_rowid + 1) {
            Some(_) => {
                self.rule_rowid += 1;
            }
            None => {
                self.useragent_rowid += 1;
                self.rule_rowid = 0;

                // the next user agent may not have any rules defined - so find
                // the next one that does
                while let Some(user_agent) = info.user_agents.get(self.useragent_rowid) {
                    if user_agent.rules.get(self.rule_rowid).is_none() {
                        self.useragent_rowid += 1;
                    } else {
                        break;
                    }
                }
            }
        }

        Ok(())
    }

    fn eof(&self) -> bool {
        return self
            .info
            .as_ref()
            .unwrap()
            .user_agents
            .get(self.useragent_rowid)
            .is_none();
    }

    fn column(&self, context: *mut sqlite3_context, i: c_int) -> Result<()> {
        let user_agents = &self.info.as_ref().unwrap().user_agents;
        let info = user_agents.get(self.useragent_rowid).unwrap();
        let rule = info.rules.get(self.rule_rowid).unwrap();
        match column(i) {
            //Some(Columns::Name) => api::result_text(context, current.name.clone())?,
            Some(Columns::UserAgent) => api::result_text(context, info.name.as_str())?,
            Some(Columns::Source) => api::result_int64(context, rule.line_number.into()),
            Some(Columns::RuleType) => match rule.rule_type {
                crate::utils::RobotsUserAgentRuleType::Allow => api::result_text(context, "allow")?,
                crate::utils::RobotsUserAgentRuleType::Disallow => {
                    api::result_text(context, "disallow")?
                }
            },
            Some(Columns::Path) => api::result_text(context, rule.value.as_str())?,
            _ => (),
        }
        Ok(())
    }

    fn rowid(&self) -> Result<i64> {
        Ok(self.rowid)
    }
}
