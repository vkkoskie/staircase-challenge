#!/usr/bin/env python3

from datetime import date
from urllib.parse import quote
from random import choice
from collections import namedtuple
from operator import attrgetter
from sys import stderr, exit
Entry = namedtuple('Entry', ['title', 'id', 'plays', 'max_plays'])

# START EDITING BELOW THIS LINE

# Your BGG user name. Only used to create a direct link to your logged plays
# for the challenge. Set to None to disable.

BGG_USER_NAME = None
#BGG_USER_NAME = "your user name here"

# This will affect the link to your logged plays page. If you aren't providing
# a user name above, it has no effect.  If None, it will assume January 1 of
# the current year.

START_DATE = None
#START_DATE = date(2022, 6, 26)

# This is the challenge level you've chosen. This will allow your ALL_GAMES
# list to be under- or overfull.

CHALLENGE_LEVEL = 10

# Must be one of the four following strings (see the challenge post for their
# meanings):

CHALLENGE_MODE = "casual"
#CHALLENGE_MODE = "intermediate"
#CHALLENGE_MODE = "hardcore"
#CHALLENGE_MODE = "antithetical"

# Your preferred way to view your progress while it's still incomplete. If
# True, games that have not yet reached their goal number of plays will prefer
# lower levels of the staircase. Counterintuitively, a lower (numerically)
# level will be higher (visually) on the staircase.
#
# For example, if a Staircase-3, with GAME1 played once, GAME2 played 3 times,
# and no third game listed:
#
# if SHIFT_LOW is False, display as
#
#     -     [empty]
#     X -   GAME1
#     X X X GAME2
#
# if SHIFT_LOW is True, display as
#
#     X     GAME1
#     - -   [empty]
#     X X X GAME2

SHIFT_LOW = False
#SHIFT_LOW = True

# Justify the staircase (and played games) to the right using blank badges.
#
# If False, a Staircase-3 will look like:
#
#     X
#     - -
#     X X -
#
# If True, a Staircase-3 will look like:
#
#         X
#       - -
#     - X X

JUSTIFY_RIGHT = False
#JUSTIFY_RIGHT = True

# Your preferred star color scheme. Valid values are:
# * "yellow" (aka gold)
# * "blue"
# * "green"
# * "pink"
# * "purple"
# * "random" - each star is a random color (no two consecutive stars the same)
# * "rowrandom" - each row is a random color (no two consecutive rows the same)

COLOR_SCHEME = "yellow"

# Fill out this list of games you'd like included in this challenge.
#
# For casual and intermediate modes, the list may be underfull (fewer items
# than the challenge level). If so, empty rows will still be added to create a
# full staircase. Similarly, it may also be overfull. In that case, the item(s)
# with the fewest plays will be discarded.
#
# Sorting by play count is handled automatically for all but antithetical mode,
# so you can order your entries however you like.
#
# Example entries below highlight different behaviors you may like to use. This
# is also a useful list to illustrate the effects of changing settings above.

ALL_GAMES = [
    # Basic Example: Title, BGG ID, Plays, Max Plays
    Entry('Fantasy Realms', 223040, 2, None),

    # Example: Use an empty string to accept BGG's default title for the given
    # ID (Morels).
    Entry("", 122298, 2, None),

    # Example: Use a None ID to list the title but not create a hyperlink to
    # the game's page.
    Entry('Marvel United', None, 4, None),

    # Example: Maximum of plays 3. Item will not appear higher than slot 3 on
    # the staircase regardless of where it would otherwise be sorted.
    Entry('Star Wars: Unlock!', 312267, 3, 3),

    # Example: Title overrides BGG link. This entry will appear with the text
    # "Dominion: Override", but link to the Dominion (id:36218) game page.
    Entry('Dominion: Override', 36218, 5, None),

    # Example: The number of plays can be larger than the challenge size. Only
    # what counts toward the challenge will be displayed.
    Entry('Res Arcana', 262712, 30, None),

    # Example: A play count of zero is valid for pre-declaring games.
    Entry('Radlands', 329082, 0, None),
]


def __shift_games_low(games: list) -> list:
    swapping = True
    while swapping:
        swapping = False
        for (i, game) in enumerate(games):
            if i > 0 and games[i - 1] is None and \
                    game is not None and game.plays <= i:
                games[i - 1] = game
                games[i] = None
                swapping = True
    return games


def __order_entry_list(games: list,
                       level: int,
                       mode: str,
                       shift_low=False) -> list:

    # Make a local copy so we don't modify the original input
    games = games[:]

    if mode == "antithetical" or mode == "hardcore":
        if level != len(games):
            print(
                "Antithetical and Hardcore modes require all games declared up front.",
                file=stderr)
            print(
                f"Your challenge level is {level} but you declared {len(games)} games.",
                file=stderr)
            exit(1)

    for (i, play_limit) in enumerate(sorted(
            [g.max_plays for g in games if g is not None and g.max_plays is not None])):
        if i >= play_limit:
            print(
                "Your challenge list contains games with maximum play constraints that make it impossible to complete.",
                file=stderr)
            exit(1)

    # sort the games by play count
    if mode != "antithetical":
        # Pre-sort by title to have a stable tie breaker on plays
        games.sort(key=attrgetter('title'))
        games.sort(key=attrgetter('plays'))

    # If more games than challenge, discard those with lowest play count
    # Otherwise, pad with empty entries
    if len(games) > level:
        games = games[-level:]
    elif len(games) < level:
        # Pad the low end of the list by default
        pad = [None] * (level - len(games))
        games = pad + games
        # If requested move entries to the lower ends of the list
        if shift_low:
            games = __shift_games_low(games)
    # If any games that have max plays have slotted above their
    # max play value, shift them back to the low end
    for max_val in range(1, len(games) + 1):
        to_reinsert = []
        for (i, game) in enumerate(games):
            if game is not None and \
                    game.max_plays is not None and \
                    game.max_plays == max_val and \
                    game.max_plays <= i:
                games.remove(game)
                to_reinsert.append(game)
        if len(to_reinsert) > 0:
            new_index = max_val - len(to_reinsert)
            if new_index < 0:
                print(f"Unexpected condition: {games}", file=stderr)
                exit(1)
            games = games[:new_index] + to_reinsert + games[new_index:]

    # for (i, g) in enumerate(games):
    #     if g is None:
    #         print(i+1, None)
    #     else:
    #         print(i+1, g.plays, g.title)
    return games


def __percent_complete(games: list) -> float:
    # assumes list is sorted and has None for empty entries
    plays = sum([min(game.plays, i + 1)
                for (i, game) in enumerate(games) if game is not None])
    level = len(games)
    # https://en.wikipedia.org/wiki/Triangular_number
    goal = level * (level + 1) / 2.0
    return (plays, goal)


def __largest_substaircase(games):
    # assumes list has already been trimmed/padded to the challenge level
    plays = sorted([g.plays for g in games if g is not None])
    if sum(plays) == 0:
        return 0
    seeking = 1
    pos = 0
    while True:
        if pos == len(plays):
            return seeking - 1
        if plays[pos] >= seeking:
            seeking += 1
        pos += 1


def __bggfmt(s: str,
             uline: bool = False,
             bold: bool = False,
             size: int = None) -> str:
    if uline:
        s = f"[u]{s}[/u]"
    if bold:
        s = f"[b]{s}[/b]"
    if size is not None:
        s = f"[size={size}]{s}[/size]"

    return s


BLUE_STAR = "[microbadge=54124]"
GREEN_STAR = "[microbadge=54126]"
PINK_STAR = "[microbadge=54122]"
PURPLE_STAR = "[microbadge=54120]"
YELLOW_STAR = "[microbadge=54118]"

CHECKED_BOX = "[microbadge=39145]"
UNCHECKED_BOX = "[microbadge=39144]"


def __random_colors(n: int) -> list:
    choices = [BLUE_STAR, GREEN_STAR, PINK_STAR, PURPLE_STAR, YELLOW_STAR]
    colors = [choice(choices)]
    while len(colors) < n:
        new_color = choice(choices)
        if new_color != colors[-1]:
            colors.append(new_color)
    return colors


def make_bgg_post(games: list,
                  level: int,
                  mode: str,
                  user_name: str = None,
                  shift_low: bool = False,
                  justify_right: bool = False,
                  color: str = "yellow",
                  start_date: date = None) -> str:

    BLANK_BADGE = "[microbadge=21088]"
    EMPTY_STAR = "[microbadge=54116]"

    lines = ["[center]"]

    games = __order_entry_list(games, level, mode, shift_low)

    # Build the title
    title = __bggfmt(f"Staircase-{level}", uline=True, bold=True, size=24)
    lines.append(title)
    title = __bggfmt(f" ({mode[0].upper()}{mode[1:]} Mode)", bold=True)
    lines.append(title)

    lines.append("")

    # Progress header
    progress_header = __bggfmt("Progress", uline=True, size=18)
    lines.append(progress_header)

    # Time stamp
    as_of = __bggfmt("Last Update:", bold=True)
    as_of += date.today().strftime(" %B %d")
    lines.append(as_of)

    # Percent complete
    (actual_plays, goal_plays) = __percent_complete(games)
    percent = "%2.1f" % (100 * actual_plays / goal_plays)
    progress = __bggfmt("Plays:", bold=True)
    progress += f" {int(actual_plays)}/{int(goal_plays)} ({percent}%)"
    lines.append(progress)

    # Highest level completed so far
    level_completed = __largest_substaircase(games)
    reached = __bggfmt("Largest Complete Staircase:", bold=True)
    reached += f" {int(level_completed)}"
    lines.append(reached)

    # Link to user's current logged plays
    if user_name is not None:
        user_name = quote(user_name)
        if start_date is None:
            start_date = date.today()
            query_start = start_date.strftime("%Y-01-01")
        else:
            query_start = start_date.strftime("%Y-%m-%d")
        query_end = start_date.strftime("%Y-12-31")
        plays_link = f'[geekurl=geekplay.php?username={user_name}&redirect=1&startdate={query_start}&enddate={query_end}&action=bygame&subtype=boardgame]My Plays[/geekurl]'
        plays_link = __bggfmt(plays_link, bold=True)
        lines.append(plays_link)

    lines.append("[/center]")

    # Generate the maximum number of colors we ever expect to use
    random_colors = __random_colors(goal_plays)

    # The actual list
    list_lines = []
    for (i, entry) in enumerate(games):
        current_slot = i + 1  # the level of this list item
        total_plays = 0 if entry is None else entry.plays
        counted_plays = min(total_plays, current_slot)
        empty_stars = [EMPTY_STAR] * (current_slot - counted_plays)

        if level >= 100:
            line_number = f'[c]({total_plays:3d}/{current_slot:3d})[/c]'
        elif level >= 10:
            line_number = f'[c]({total_plays:2d}/{current_slot:2d})[/c]'
        else:
            line_number = f'[c]({current_slot})[/c]'

        if color == "random":
            filled_stars = random_colors[:counted_plays]
            random_colors = random_colors[counted_plays:]
        elif color == "rowrandom":
            filled_stars = random_colors[:1] * counted_plays
            random_colors = random_colors[1:]
        elif color == "yellow":
            filled_stars = [YELLOW_STAR] * counted_plays
        elif color == "blue":
            filled_stars = [BLUE_STAR] * counted_plays
        elif color == "green":
            filled_stars = [GREEN_STAR] * counted_plays
        elif color == "pink":
            filled_stars = [PINK_STAR] * counted_plays
        elif color == "purple":
            filled_stars = [PURPLE_STAR] * counted_plays
        else:
            print(f'Invalid COLOR_SCHEME value "{color}"', file=stderr)
            exit(1)

        if counted_plays == current_slot:
            check_box = CHECKED_BOX
        else:
            check_box = UNCHECKED_BOX

        if entry is None:
            # Empty row of stars (no game assigned)
            game_name = ""
        elif entry.id is not None:
            # Given string (possibly empty) with ID hyperlink
            game_name = f'[thing={entry.id}]{entry.title}[/thing]'
        elif entry.title != "":
            # Bare string with no hyperlink
            game_name = entry.title
        else:
            print(
                "Cannot list a game with neither a title nor a BGG ID",
                file=stderr)
            exit(1)

        if justify_right:
            blank_spaces = [BLANK_BADGE] * (level - current_slot)
            line = " ".join(blank_spaces + empty_stars +
                            filled_stars + [line_number, check_box, game_name])
        else:
            line = " ".join([check_box, line_number] +
                            filled_stars + empty_stars + [game_name])

        list_lines.append(line.strip())

    list_lines = "\n" + "\n".join(list_lines) + "\n"
    lines.append(__bggfmt(list_lines, size=14))

    return lines


def print_bgg_post():
    post = make_bgg_post(
        ALL_GAMES,
        CHALLENGE_LEVEL,
        CHALLENGE_MODE,
        user_name=BGG_USER_NAME,
        shift_low=SHIFT_LOW,
        justify_right=JUSTIFY_RIGHT,
        color=COLOR_SCHEME,
        start_date=START_DATE
    )

    for line in post:
        print(line)


if __name__ == '__main__':
    print_bgg_post()
