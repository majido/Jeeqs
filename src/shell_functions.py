# updates the challenge stats

all_challenge = Challenge.all().fetch(100)
for ch in all_challenge:
    ch.num_jeeqsers_submitted= Jeeqser_Challenge.all().filter('challenge = ', ch).count()
    ch.num_jeeqsers_solved = Jeeqser_Challenge.all().filter('challenge = ', ch).filter('status = ', 'correct').count()
    ch.put()