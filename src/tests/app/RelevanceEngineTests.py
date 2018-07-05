import unittest

from appserver.rules.RelevanceEngine import RelevanceEngine
from appserver.rules.StoryRelevance import StoryRelevance


class RelevanceEngineTests(unittest.TestCase):

    def test_relevance_engine_low_rules(self):
        story_relevance = StoryRelevance(1, 0, 1, 1, 1)
        RelevanceEngine.run_rule(story_relevance)

        expected_points = 1 * 1 + 5 + 1 * 2 + 1 * 0.5 - 1.5

        self.assertEqual(story_relevance.get_relevance_points(), expected_points)

    def test_relevance_engine_medium_rules(self):
        story_relevance = StoryRelevance(10, 0, 10, 10, 1)
        RelevanceEngine.run_rule(story_relevance)

        expected_points = 10 * 0.4 + 5 + 10 * 0.8 + 10 * 0.2 - 1.5

        self.assertEqual(story_relevance.get_relevance_points(), expected_points)

    def test_relevance_engine_high_rules(self):
        story_relevance = StoryRelevance(100, 0, 100, 100, 1)
        RelevanceEngine.run_rule(story_relevance)

        expected_points = 100 * 0.12 + 5 + 100 * 0.24 + 100 * 0.06 - 1.5

        self.assertEqual(story_relevance.get_relevance_points(), expected_points)

    def test_relevance_engine_multiple_stories_rule(self):
        story_relevance = StoryRelevance(0, 10, 0, 0, 0)
        RelevanceEngine.run_rule(story_relevance)

        expected_points = -3 * 10

        self.assertEqual(story_relevance.get_relevance_points(), expected_points)
