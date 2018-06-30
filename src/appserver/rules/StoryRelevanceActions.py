from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_NUMERIC


class StoryRelevanceActions(BaseActions):

    def __init__(self, story_relevance):
        self.story_relevance = story_relevance

    @rule_action(params={'friendship_rate': FIELD_NUMERIC})
    def add_friendship_points(self, friendship_rate):
        relevance_points = friendship_rate * self.story_relevance.total_friends
        self.story_relevance.add_relevance_points(relevance_points)

    @rule_action(params={'points_to_add': FIELD_NUMERIC})
    def first_publication_points(self, points_to_add):
        self.story_relevance.add_relevance_points(points_to_add)

    @rule_action(params={'penalty_rate': FIELD_NUMERIC})
    def penalty_multiple_posts(self, penalty_rate):
        penalty_points = -penalty_rate * self.story_relevance.total_publications
        self.story_relevance.add_relevance_points(penalty_points)

    @rule_action(params={'comments_rate': FIELD_NUMERIC})
    def add_comments_points(self, comments_rate):
        relevance_points = comments_rate * self.story_relevance.total_comments
        self.story_relevance.add_relevance_points(relevance_points)

    @rule_action(params={'reactions_rate': FIELD_NUMERIC})
    def add_reactions_points(self, reactions_rate):
        relevance_points = reactions_rate * self.story_relevance.total_reactions
        self.story_relevance.add_relevance_points(relevance_points)

    @rule_action(params={'decay_rate': FIELD_NUMERIC})
    def time_decay(self, decay_rate):
        penalty_points = -decay_rate * self.story_relevance.total_hours_passed
        self.story_relevance.add_relevance_points(penalty_points)
