mod robotstxt_rules;
mod robotstxt_user_agents;
mod utils;

use sqlite_loadable::{api, define_scalar_function, Error, Result};
use sqlite_loadable::{define_table_function, prelude::*};

use robotstxt::DefaultMatcher;

use crate::{robotstxt_rules::RulesTable, robotstxt_user_agents::UserAgentsTable};
// robotstxt_version() -> 'v0.1.0'
pub fn robotstxt_version(
    context: *mut sqlite3_context,
    _values: &[*mut sqlite3_value],
) -> Result<()> {
    api::result_text(context, format!("v{}", env!("CARGO_PKG_VERSION")))?;
    Ok(())
}
pub fn robotstxt_matches(
    context: *mut sqlite3_context,
    values: &[*mut sqlite3_value],
) -> Result<()> {
    let robotstxt = api::value_text(values.get(0).ok_or_else(|| Error::new_message("TODO"))?)
        .map_err(|_| Error::new_message("TODO"))?;
    let useragent = api::value_text(values.get(1).ok_or_else(|| Error::new_message("TODO"))?)
        .map_err(|_| Error::new_message("TODO"))?;
    let url = api::value_text(values.get(2).ok_or_else(|| Error::new_message("TODO"))?)
        .map_err(|_| Error::new_message("TODO"))?;
    let mut matcher = DefaultMatcher::default();
    let result = matcher.one_agent_allowed_by_robots(robotstxt, useragent, url);
    api::result_bool(context, result);
    Ok(())
}

pub fn robotstxt_debug(
    context: *mut sqlite3_context,
    _values: &[*mut sqlite3_value],
) -> Result<()> {
    api::result_text(
        context,
        format!(
            "Version: v{}
Source: {}
",
            env!("CARGO_PKG_VERSION"),
            env!("GIT_HASH")
        ),
    )?;
    Ok(())
}

#[sqlite_entrypoint]
pub fn sqlite3_robotstxt_init(db: *mut sqlite3) -> Result<()> {
    define_scalar_function(
        db,
        "robotstxt_version",
        0,
        robotstxt_version,
        FunctionFlags::UTF8 | FunctionFlags::DETERMINISTIC,
    )?;
    define_scalar_function(
        db,
        "robotstxt_debug",
        0,
        robotstxt_debug,
        FunctionFlags::UTF8 | FunctionFlags::DETERMINISTIC,
    )?;
    define_scalar_function(
        db,
        "robotstxt_matches",
        3,
        robotstxt_matches,
        FunctionFlags::UTF8 | FunctionFlags::DETERMINISTIC,
    )?;

    define_table_function::<UserAgentsTable>(db, "robotstxt_user_agents", None)?;
    define_table_function::<RulesTable>(db, "robotstxt_rules", None)?;
    Ok(())
}
