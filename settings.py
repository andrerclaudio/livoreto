"""
All system settings are here.
"""
import time


class FunctionalSystemSettings(object):

    def __init__(self):
        # --------------------------------------------------------------------------------
        """ ----------- Mode work options -----------
        Development and Cloud     = 'dev&cloud'
        Development and Raspberry = 'dev&rasp'
        Production and Cloud      = 'prod&cloud'
        Production and Raspberry  = 'prod&rasp'
        ----------------------------------------- """
        self.WORK_MODE = 'prod&cloud'
        # --------------------------------------------------------------------------------
        """
        Recommendations System Settings.
        """
        self.MINUTES = 30
        self.run_at_initialization = True
        self.running_recommender = True
        self.last_recommendation_run = time.time()
        self.DELTA = 60 * self.MINUTES
        # --------------------------------------------------------------------------------
        """
        Emoji list used in application. It is necessary to run some filters.
        """
        self.emoji_list = ['📋', '📚', '📖']


settings = FunctionalSystemSettings()
