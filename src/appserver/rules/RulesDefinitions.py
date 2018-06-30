class RulesDefinitions(object):

    @staticmethod
    def get_rules():
        return [RulesDefinitions.__low_friendship_rule(), RulesDefinitions.__medium_friendship_rule(),
                RulesDefinitions.__high_friendship_rule()]


    @staticmethod
    def __low_friendship_rule():
        return {
            "conditions": {
                "all": [
                    {
                        "name": "total_friends",
                        "operator": "less_than",
                        "value": 5
                    }
                ]
            },
            "actions": [
                {
                    "name": "add_friendship_points",
                    "params": {
                        "friendship_points": 1
                    }
                }
            ]
        }

    @staticmethod
    def __medium_friendship_rule():
        return {
            "conditions": {
                "all": [
                    {
                        "name": "total_friends",
                        "operator": "less_than",
                        "value": 20
                    },
                    {
                        "name": "total_friends",
                        "operator": "more_than",
                        "value": 4
                    }
                ]
            },
            "actions": [
                {
                    "name": "add_friendship_points",
                    "params": {
                        "friendship_points": 0.4
                    }
                }
            ]
        }

    @staticmethod
    def __high_friendship_rule():
        return {
            "conditions": {
                "all": [
                    {
                        "name": "total_friends",
                        "operator": "more_than",
                        "value": 19
                    }
                ]
            },
            "actions": [
                {
                    "name": "add_friendship_points",
                    "params": {
                        "friendship_points": 0.12
                    }
                }
            ]
        }
