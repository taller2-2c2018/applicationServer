from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_NUMERIC


class StoryRelevanceActions(BaseActions):

    def __init__(self, story_relevance):
        self.story_relevance = story_relevance

    @rule_action(params={"friendship_points": FIELD_NUMERIC})
    def add_friendship_points(self, friendship_points):
        relevance_points = friendship_points * self.story_relevance.total_friends
        self.story_relevance.add_relevance_points(relevance_points)
