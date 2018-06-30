class StoryRelevance:

    def __init__(self, total_friends, total_publications, total_comments, total_reactions, total_hours_passed):
        self.total_friends = total_friends
        self.total_publications = total_publications
        self.total_comments = total_comments
        self.total_reactions = total_reactions
        self.total_hours_passed = total_hours_passed
        self.relevance_points = 0

    def add_relevance_points(self, relevance_points):
        self.relevance_points += relevance_points

    def get_relevance_points(self):
        return self.relevance_points
