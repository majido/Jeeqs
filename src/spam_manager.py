"""
A class for fighting spam.

"""

from datetime import timedelta
from datetime import datetime
from google.appengine.api import users


class FlaggingLimitReachedError(Exception):
    """
    Thrown if the user has already flagged more than limit.
    """
    pass

class spam_manager:
    # flag threshold for deleting a submission
    submission_flag_threshold = 3

    # flag threshold for deleting a feedback
    feedback_flag_threshold = 3

    # if the author has this many flagged content, he/she will be suspended for one day per violation.
    author_suspension_threshold = 3

    # number of flagging actions a user can perform in a single day
    flaging_limit_per_day = 5


    @classmethod
    def flag_author(cls, jeeqser):
        """
        This is invoked when an author's submission or feedback is flagged by enough people.
        """
        jeeqser.total_flag_count += 1
        jeeqser.unaccounted_flag_count += 1
        if jeeqser.unaccounted_flag_count >= spam_manager.author_suspension_threshold:
            jeeqser.unaccounted_flag_count = 0
            oneday = timedelta(days=1)
            if (jeeqser.suspended_until):
                jeeqser.suspended_until = jeeqser.suspended_until + oneday
            else:
                jeeqser.suspended_until = datetime.now() + oneday
        jeeqser.put()

    @classmethod
    def check_flag_limit(cls, jeeqser):
        """
        Checks whether jeeqser is over-limit for flagging and throws FlaggingLimitReachedError if so. If not, increase a counter.
        """

        if users.is_current_user_admin():
            return 1000

        now = datetime.now()
        if not jeeqser.last_flagged_on or jeeqser.last_flagged_on.date() < now.date():
            jeeqser.last_flagged_on = now
            jeeqser.num_flagged_today = 1
            jeeqser.put()
            return spam_manager.flaging_limit_per_day - 1
        elif jeeqser.num_flagged_today >= spam_manager.flaging_limit_per_day:
            return -1
        else:
            jeeqser.last_flagged_on = now
            jeeqser.num_flagged_today = jeeqser.num_flagged_today + 1
            jeeqser.put()
            return spam_manager.flaging_limit_per_day - jeeqser.num_flagged_today
