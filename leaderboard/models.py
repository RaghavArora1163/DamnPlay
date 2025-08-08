class LeaderboardEntry:
    def __init__(self, user_id, username, score, rank=None, contest_id=None, timestamp=None):
        self.user_id = user_id
        self.username = username
        self.score = score
        self.rank = rank
        self.contest_id = contest_id  # Link to the contest
        self.timestamp = timestamp  # For historical data

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "score": self.score,
            "rank": self.rank,
            "contest_id": self.contest_id,
            "timestamp": self.timestamp,
        }