use robotstxt::RobotsParseHandler;

#[derive(Debug, Clone)]
pub(crate) enum RobotsUserAgentRuleType {
    Allow,
    Disallow,
}
#[derive(Debug, Clone)]
pub(crate) struct RobotsUserAgentRule {
    pub(crate) rule_type: RobotsUserAgentRuleType,
    pub(crate) value: String,
    pub(crate) line_number: u32,
}

#[derive(Debug, Clone)]
pub(crate) struct RobotsUserAgentInfo {
    pub(crate) name: String,
    pub(crate) line_number: u32,
    pub(crate) rules: Vec<RobotsUserAgentRule>,
}
#[derive(Debug, Default, Clone)]
pub(crate) struct RobotsInfo {
    pub(crate) user_agents: Vec<RobotsUserAgentInfo>,
    current_user_agent: Option<RobotsUserAgentInfo>,
}

impl RobotsInfo {}

impl RobotsParseHandler for RobotsInfo {
    fn handle_robots_start(&mut self) {}

    fn handle_robots_end(&mut self) {
        if let Some(prev) = self.current_user_agent.take() {
            self.user_agents.push(prev);
        }
    }

    fn handle_user_agent(&mut self, line_num: u32, user_agent: &str) {
        let current = RobotsUserAgentInfo {
            name: user_agent.to_owned(),
            line_number: line_num,
            rules: vec![],
        };
        if let Some(prev) = self.current_user_agent.take() {
            self.user_agents.push(prev);
        }
        self.current_user_agent = Some(current);
    }

    fn handle_allow(&mut self, line_num: u32, value: &str) {
        let current = self.current_user_agent.as_mut().unwrap();
        current.rules.push(RobotsUserAgentRule {
            rule_type: RobotsUserAgentRuleType::Allow,
            value: value.to_owned(),
            line_number: line_num,
        });
    }

    fn handle_disallow(&mut self, line_num: u32, value: &str) {
        let current = self.current_user_agent.as_mut().unwrap();
        current.rules.push(RobotsUserAgentRule {
            rule_type: RobotsUserAgentRuleType::Disallow,
            value: value.to_owned(),
            line_number: line_num,
        });
    }

    fn handle_sitemap(&mut self, line_num: u32, value: &str) {
        //println!("sitemap {} {}", line_num, value);
    }

    // Any other unrecognized name/v pairs.
    fn handle_unknown_action(&mut self, line_num: u32, action: &str, value: &str) {
        //println!("unkown {} {} {}", line_num, action, value);
    }
}

pub(crate) fn parse(source: &str) -> RobotsInfo {
    let mut info = RobotsInfo::default();
    robotstxt::parse_robotstxt(source, &mut info);
    info
}
