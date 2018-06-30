from business_rules.variables import BaseVariables, numeric_rule_variable


class StoryRelevanceVariables(BaseVariables):

    def __init__(self, story_relevance):
        self.story_relevance = story_relevance

    @numeric_rule_variable
    def total_friends(self):
        return self.story_relevance.total_friends
