import random


def get_completion_encouragement():
    messages = [
        "Great job! Keep up the momentum!",
        "You're making progress one habit at a time!",
        "Way to go! Building strong habits takes commitment!",
        "Excellent work! Small steps lead to big changes!",
        "Amazing! You're one step closer to your goals!",
    ]
    return random.choice(messages)


def get_streak_encouragement(streak, is_weekly=False):
    if is_weekly:
        if streak >= 52:
            messages = [
                f"A whole year - {streak} weeks of incredible dedication!",
                "52 weeks of excellence! You're truly unstoppable!",
                "One full year! You've made this habit a part of who you are!",
            ]
        elif streak >= 12:
            messages = [
                f"Three months strong - {streak} weeks of dedication!",
                "A quarter year of consistency! Keep going!",
                f"{streak} weeks of commitment - you're building something great!",
            ]
        elif streak >= 4:
            messages = [
                f"One month milestone - {streak} fantastic weeks!",
                "Four weeks of dedication! You're establishing a real routine!",
                "A month of progress! This is becoming a true habit!",
            ]
        else:
            messages = [
                f"{streak} weeks and counting - you're on your way!",
                f"Week {streak} complete - keep the momentum going!",
                f"{streak} weeks of progress - every week counts!",
            ]
    else:
        if streak >= 100:
            messages = [
                f"Phenomenal! {streak} days of unwavering commitment!",
                f"Triple digits - {streak} days of excellence!",
                f"You're an inspiration! {streak} days of dedication!",
            ]
        elif streak >= 30:
            messages = [
                f"A month of success - {streak} fantastic days!",
                f"Outstanding dedication! {streak} days and counting!",
                f"Look at you go - {streak} days of positive change!",
            ]
        elif streak == 7:
            messages = [
                f"A full week of dedication! {streak} days strong!",
                f"{streak} days of progress - you're building momentum!",
                f"Great work on maintaining your {streak}-day streak!",
            ]
        else:
            messages = [
                f"{streak} days and counting - keep it up!",
                f"Day {streak} complete - stay consistent!",
                f"{streak} days of progress - every day counts!",
            ]
    return random.choice(messages)


def get_completion_rate_encouragement(rate):
    if rate >= 0.9:
        messages = [
            f"Outstanding! {rate:.0%} completion rate - absolute excellence!",
            f"Incredible consistency with {rate:.0%} completion!",
            f"Top-tier performance at {rate:.0%}! Keep it up!",
        ]
    elif rate >= 0.7:
        messages = [
            f"Great work maintaining a {rate:.0%} completion rate!",
            f"Solid performance at {rate:.0%}! You're doing great!",
            f"{rate:.0%} completion - getting stronger every day!",
        ]
    else:
        messages = [
            "Every completion counts - keep pushing forward!",
            "Progress is progress, no matter how small!",
            "Keep going - consistency builds success!",
        ]
    return random.choice(messages)
