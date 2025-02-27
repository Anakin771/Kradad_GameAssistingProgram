"""
***********************************************

Author: MontyGUI

Description
This script includes every functions that revolves
around boss's stats, such as generating a single boss stats,
generating group boss, etc.

***********************************************
"""
import math
import random


# Boss HP-by-LV Multiplier
EARLY_BOSS_HP_MTP = 700
MID_BOSS_HP_MTP = 850
LATE_BOSS_HP_MTP = 1000

# Multi-Boss-Fight Stats-Down Multiplier
MULTIPLE_BOSS_MTP = 0.8

# Rewards Multiplier
EARLY_XP_MULTIPLIER = 1300
MID_XP_MULTIPLIER = 1400
LATE_XP_MULTIPLIER = 1500
MONEY_MULTIPLIER = 100

# Difficulty names-to-rate tables...
DIFF_TO_LV_MAPPING = {
    "noob": -5,
    "easy": -3,
    "normal": 0,
    "hard": 3,
    "hardcore": 6
}
DIFF_TO_COIN_MAPPING = {
    "noob": -5,
    "easy": -1,
    "normal": 0,
    "hard": 3,
    "hardcore": 6
}
DIFF_TO_HP_MAPPING = {
    "noob": -2,
    "easy": -1,
    "normal": 0,
    "hard": 3,
    "hardcore": 8
}
DIFF_TO_ITEM_MAPPING = {
    "noob": "0",
    "easy": "1",
    "normal": "1 or 2",
    "hard": "2",
    "hardcore": "3"
}


def round_half_up(n, decimals=0):
    mtp = 10 ** decimals
    return math.floor(n * mtp + 0.5) / mtp


def round_basic(n, decimals=0):
    rounded_abs = round_half_up(abs(n), decimals)
    return math.copysign(rounded_abs, n)


def random_boss_stat(party_avg_lv, player_num, diff=None, show_stat=True):

    input_diff = True

    # Default value for diff if unspecified
    if diff is None:
        input_diff = False
        diff = "normal"

    # Adjust Difficulty
    hp_diff_rate, boss_lv = adjust_difficulty(party_avg_lv, diff)
    if hp_diff_rate is None or boss_lv is None:
        return

    # Determine Boss' HP
    boss_hp = calculate_boss_hp(boss_lv, party_avg_lv, hp_diff_rate, player_num)

    # Calculate Reward
    xp_reward, money_reward, item_reward = calculate_reward(boss_lv, party_avg_lv, diff)

    # Determine Boss Stats' Roll Point
    boss_roll_pt = boss_lv if boss_lv >= 10 else boss_lv * 5
    boss_stat_mtp = 100 if boss_lv >= 10 else 20

    # Create Boss Dictionary for returning
    boss = {
        "DIFFICULTY": diff,
        "LV": boss_lv,
        "HP": boss_hp,
        "PATK": 0,
        "MATK": 0,
        "PDEF": 0,
        "MDEF": 0
    }

    # Roll Choices
    roll_choices = ["PATK", "MATK", "PDEF", "MDEF"]

    # Randomize Stat Points
    stats_rand = random.choices(roll_choices, k=boss_roll_pt)
    for stat in stats_rand:
        boss[stat] += boss_stat_mtp

    # Show stats if set enabled
    if show_stat:
        print("-------------------------------------------------")
        print(f" BOSS - LV. {boss_lv}")
        if input_diff:
            print(f" {diff.upper()} DIFFICULTY")
        print()
        print(" STATS:")
        print(f" HP: {boss_hp}")
        print(f" P. ATK: {boss['PATK']}")
        print(f" M. ATK: {boss['MATK']}")
        print(f" P. DEF: {int(boss['PDEF'] / 2)}")
        print(f" M. DEF: {int(boss['MDEF'] / 2)}")
        print("-------------------------------------------------")
        print(" Rewards* :")
        print(
            f"  • {xp_reward} XP\n"
            f"  • {money_reward} (C)\n"
            f"  • {item_reward} Item(s)\n"
        )
        print(" * Rewards on a scenario case that no one died,\n"
              "and no +20% Bonus from declining dropped item.")
        print("-------------------------------------------------")

    return boss


def random_boss_stat_multi(party_avg_lv, player_num, qty, diff=None, show_stat=True):

    input_diff = True

    # Default value for diff if unspecified
    if diff is None:
        input_diff = False
        diff = "normal"

    hp_diff_rate, boss_lv = adjust_difficulty(party_avg_lv, diff)

    # Calculate Reward
    xp_reward, money_reward, item_reward = calculate_reward(boss_lv, party_avg_lv, diff)

    # Determine Bosses' HP
    boss_hp = int(calculate_boss_hp(boss_lv, party_avg_lv, hp_diff_rate, player_num) / 3)

    # Initial Variable Setup
    boss_list = []
    count = 0
    reduce_mtp = 0.8

    while count < qty:
        single_boss_stat = random_boss_stat(party_avg_lv, player_num, diff=diff, show_stat=False)
        current_boss = {
            "LV": single_boss_stat["LV"],
            "DIFFICULTY": diff,
            "HP": boss_hp,
            "PATK": int(round_basic(single_boss_stat["PATK"] * reduce_mtp, -1)),
            "MATK": int(round_basic(single_boss_stat["MATK"] * reduce_mtp, -1)),
            "PDEF": int(round_basic(single_boss_stat["PDEF"] * reduce_mtp, -1)),
            "MDEF": int(round_basic(single_boss_stat["MDEF"] * reduce_mtp, -1))
        }

        boss_list.append(current_boss)
        count += 1

    if show_stat:
        boss_count = 1

        print("**********************************************")
        print("     -------- MULTI-BOSS FIGHT --------    ")
        if input_diff:
            print(f" {diff.upper()} DIFFICULTY")
        print()
        for boss in boss_list:
            print(f" Boss #{boss_count} Stats:")
            for stat, value in boss.items():
                # Skip Difficulty (This is added for compatibility with Graphical Edition)
                if stat == "DIFFICULTY":
                    continue

                if stat == "LV":
                    print(f" LV. {value}")
                elif stat == "PDEF" or stat == "MDEF":
                    print(f" {stat}: {int(value / 2)}")
                else:
                    print(f" {stat}: {value}")

            print()
            boss_count += 1
        print("-------------------------------------------------")
        print(" Rewards* :")
        print(
            f"  • {xp_reward} XP\n"
            f"  • {money_reward} (C)\n"
            f"  • {item_reward} Item(s)\n"
        )
        print(" * Rewards on a scenario case that no one died,\n"
              "and no +20% Bonus from declining dropped item.\n")
        print("**********************************************")

    return boss_list


def calculate_boss_hp(boss_lv, pty_avg, hp_diff_rate, player_num):
    if boss_lv <= 30:
        boss_hp = (pty_avg + hp_diff_rate) * player_num * EARLY_BOSS_HP_MTP
    elif boss_lv <= 60:
        boss_hp = (pty_avg + hp_diff_rate) * player_num * MID_BOSS_HP_MTP
    else:
        boss_hp = (pty_avg + hp_diff_rate) * player_num * LATE_BOSS_HP_MTP

    return int(boss_hp)


def calculate_xp(boss_lv):
    if boss_lv <= 30:
        xp_reward = boss_lv * EARLY_XP_MULTIPLIER
    elif boss_lv <= 60:
        xp_reward = boss_lv * MID_XP_MULTIPLIER
    else:
        xp_reward = boss_lv * LATE_XP_MULTIPLIER

    return int(xp_reward)


def adjust_difficulty(prty_avg, diff, show_text="True"):
    # Get Boss LV Difficulty Rate
    lv_diff_rate = DIFF_TO_LV_MAPPING.get(diff, 0)

    # Get Boss HP Difficulty Rate
    hp_diff_rate = DIFF_TO_HP_MAPPING.get(diff, 0)

    # Find Bosses' Real LV
    boss_lv = prty_avg + lv_diff_rate

    # If calculated LV is 0 or less, flag an error an find the floor difficulty for that party.
    if boss_lv <= 0:
        least_diff = ""
        for diff_name, lv in DIFF_TO_LV_MAPPING.items():
            if prty_avg + lv > 0:
                least_diff = diff_name
                break

        if show_text:
            print(" Error: Too low difficulty!")
            print(f" For LV {prty_avg} party,"
                  f" Boss Difficulty must be at least on {least_diff.capitalize()}.")
        return None, None

    return hp_diff_rate, boss_lv


def calculate_reward(boss_lv, prty_avg, diff):
    # Calculate XP Reward
    xp_reward = calculate_xp(boss_lv)

    # Get Boss Coin Reward Difficulty Rate
    money_diff_rate = DIFF_TO_COIN_MAPPING.get(diff, 0)

    # Calculate Money Reward
    money_reward = (prty_avg + money_diff_rate) * MONEY_MULTIPLIER

    # Get Boss Item Reward Difficulty Rate
    item_reward = DIFF_TO_ITEM_MAPPING.get(diff, 0)

    return xp_reward, money_reward, item_reward
