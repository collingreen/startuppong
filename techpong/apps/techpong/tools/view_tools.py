import json


def create_sparklines(player):
    """Creates strings for rendering sparklines based
    on a player's cached information."""

    # results sparkline
    cached_results = json.loads(player.cached_results or '[]')
    player.results_sparkline = ','.join(
            ['1' if m['winner'] else '-1' for m in cached_results])

    cached_rating_changes = json.loads(player.cached_rating_changes or '[]')
    player.ratings_sparkline = ','.join(
            ['%.02f' % m['rating'] for m in cached_rating_changes])

    cached_rank_changes = json.loads(player.cached_rank_changes or '[]')
    player.rank_sparkline = ','.join(
            [str(m['rank']) for m in cached_rank_changes])
