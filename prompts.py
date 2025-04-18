def get_classification_prompt(query: str) -> str:
    return f"""You are a classifier that assigns football-related questions to categories:
Options: live_score, player_stats, team_stats, fixture

Examples:
Q: What is the current score of the Manchester United match?
A: live_score

Q: Tell me Haaland’s stats this season.
A: player_stats

Q: How did Real Madrid perform in 2021?
A: team_stats

Q: Who is Manchester City playing next week?
A: fixture

Q: {query}
A:"""
