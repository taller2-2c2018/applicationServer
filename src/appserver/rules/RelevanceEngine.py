from business_rules import run_all
from appserver.rules.StoryRelevanceVariables import StoryRelevanceVariables
from appserver.rules.StoryRelevanceActions import StoryRelevanceActions
from appserver.rules.RulesDefinitions import RulesDefinitions

rules = RulesDefinitions.get_rules()


class RelevanceEngine(object):

    @staticmethod
    def run_rule(story_relevance):
        run_all(rule_list=rules,
                defined_variables=StoryRelevanceVariables(story_relevance),
                defined_actions=StoryRelevanceActions(story_relevance),
                stop_on_first_trigger=True
                )
