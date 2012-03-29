"""
A class for fighting spam.

"""

from datetime import timedelta
from datetime import datetime

class spam_manager:
    # flag threshold for deleting a submission
    submission_flag_threshold = 3;

    # flag threshold for deleting a feedback
    feedback_flag_threshold = 3;

    # if the author has this many flagged content, he/she will be suspended for one day per violation.
    author_suspension_threshold = 1;

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
