class RulesDefinitions(object):

    @staticmethod
    def get_rules():
        return [RulesDefinitions.__low_friendship_rule(), RulesDefinitions.__medium_friendship_rule(),
                RulesDefinitions.__high_friendship_rule(), RulesDefinitions.__first_post_of_the_day(),
                RulesDefinitions.__multiple_posts_a_day(), RulesDefinitions.__low_comments_rule(),
                RulesDefinitions.__medium_comments_rule(), RulesDefinitions.__high_comments_rule(),
                RulesDefinitions.__low_reactions_rule(), RulesDefinitions.__medium_reactions_rule(),
                RulesDefinitions.__high_reactions_rule(), RulesDefinitions.__time_decay_rule()]

    @staticmethod
    def __low_friendship_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_friends',
                        'operator': 'less_than',
                        'value': 5
                    }
                ]
            },
            'actions': [
                {
                    'name': 'add_friendship_points',
                    'params': {
                        'friendship_rate': 1
                    }
                }
            ]
        }

    @staticmethod
    def __medium_friendship_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_friends',
                        'operator': 'less_than',
                        'value': 20
                    },
                    {
                        'name': 'total_friends',
                        'operator': 'greater_than',
                        'value': 4
                    }
                ]
            },
            'actions': [
                {
                    'name': 'add_friendship_points',
                    'params': {
                        'friendship_rate': 0.4
                    }
                }
            ]
        }

    @staticmethod
    def __high_friendship_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_friends',
                        'operator': 'greater_than',
                        'value': 19
                    }
                ]
            },
            'actions': [
                {
                    'name': 'add_friendship_points',
                    'params': {
                        'friendship_rate': 0.12
                    }
                }
            ]
        }

    @staticmethod
    def __first_post_of_the_day():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_publications',
                        'operator': 'equal_to',
                        'value': 0
                    }
                ]
            },
            'actions': [
                {
                    'name': 'first_publication_points',
                    'params': {
                        'points_to_add': 5
                    }
                }
            ]
        }

    @staticmethod
    def __multiple_posts_a_day():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_publications',
                        'operator': 'greater_than',
                        'value': 0
                    }
                ]
            },
            'actions': [
                {
                    'name': 'penalty_multiple_posts',
                    'params': {
                        'penalty_rate': 3
                    }
                }
            ]
        }

    @staticmethod
    def __low_comments_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_comments',
                        'operator': 'less_than',
                        'value': 5
                    }
                ]
            },
            'actions': [
                {
                    'name': 'add_comments_points',
                    'params': {
                        'comments_rate': 2
                    }
                }
            ]
        }

    @staticmethod
    def __medium_comments_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_comments',
                        'operator': 'less_than',
                        'value': 20
                    },
                    {
                        'name': 'total_comments',
                        'operator': 'greater_than',
                        'value': 4
                    }
                ]
            },
            'actions': [
                {
                    'name': 'add_comments_points',
                    'params': {
                        'comments_rate': 0.8
                    }
                }
            ]
        }

    @staticmethod
    def __high_comments_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_comments',
                        'operator': 'greater_than',
                        'value': 19
                    }
                ]
            },
            'actions': [
                {
                    'name': 'add_comments_points',
                    'params': {
                        'comments_rate': 0.24
                    }
                }
            ]
        }

    @staticmethod
    def __low_reactions_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_reactions',
                        'operator': 'less_than',
                        'value': 5
                    }
                ]
            },
            'actions': [
                {
                    'name': 'add_reactions_points',
                    'params': {
                        'reactions_rate': 0.5
                    }
                }
            ]
        }

    @staticmethod
    def __medium_reactions_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_reactions',
                        'operator': 'less_than',
                        'value': 20
                    },
                    {
                        'name': 'total_reactions',
                        'operator': 'greater_than',
                        'value': 4
                    }
                ]
            },
            'actions': [
                {
                    'name': 'add_reactions_points',
                    'params': {
                        'reactions_rate': 0.2
                    }
                }
            ]
        }

    @staticmethod
    def __high_reactions_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_reactions',
                        'operator': 'greater_than',
                        'value': 19
                    }
                ]
            },
            'actions': [
                {
                    'name': 'add_reactions_points',
                    'params': {
                        'reactions_rate': 0.06
                    }
                }
            ]
        }

    @staticmethod
    def __time_decay_rule():
        return {
            'conditions': {
                'all': [
                    {
                        'name': 'total_hours_passed',
                        'operator': 'greater_than_or_equal_to',
                        'value': 0
                    }
                ]
            },
            'actions': [
                {
                    'name': 'time_decay',
                    'params': {
                        'decay_rate': 1.5
                    }
                }
            ]
        }