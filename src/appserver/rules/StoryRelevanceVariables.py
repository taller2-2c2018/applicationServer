from business_rules.variables import BaseVariables, numeric_rule_variable


class StoryRelevanceVariables(BaseVariables):

    def __init__(self, story_relevance):
        self.story_relevance = story_relevance

    @numeric_rule_variable
    def total_friends(self):
        return self.story_relevance.total_friends

    @numeric_rule_variable
    def total_publications(self):
        return self.story_relevance.total_publications

    @numeric_rule_variable
    def total_comments(self):
        return self.story_relevance.total_comments

    @numeric_rule_variable
    def total_reactions(self):
        return self.story_relevance.total_reactions

    @numeric_rule_variable
    def total_hours_passed(self):
        return self.story_relevance.total_hours_passed
