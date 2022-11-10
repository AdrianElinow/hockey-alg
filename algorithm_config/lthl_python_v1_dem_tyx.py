
def contract( ranges, player ):


    """values = [ val  for attribute in player.attributes.keys() 
                                for (low, high), val in ranges[attribute].items() 
                                if low <= player.attributes[attribute] <= high ]"""

    #average = sum(values)/len(values)

    #""" # list-comprehention equivalent expanded for-loop version
    values = []

    for attribute in ranges:

        # iterate through each attribute bracket
        for rng, val in ranges[attribute].items():
            low, high = rng 

            # check if value is within range
            if low <= player.attributes[attribute] <= high:
                values.append(val)

    average = sum(values)/len(values)
    #"""

    return average

def performance_bonus( factors, player, goalie=False ):
 

    # multiply each category by relevant factor
    bonuses = { category: (score * factors[category]) for category,score in player.performance.items() }
 
    """
    bonuses = {}
    for category,score in player.performance.items():
        bonuses[category] = score*factors[category]
    """

    if goalie:
        # single value correction for "GAA"
        bonuses["GAA"] = 500000 - bonuses["GAA"]

    return sum(bonuses.values())

def escalator( escalator, player, debug=False):
    
    total_factor = 0
    for (age_low, age_high),lookup in escalator.items():

        if age_low <= player.age <= age_high:


            for factor,table in lookup.items():

                try:
                    if factor == "BASE":
                        if(debug):
                            print(factor, table[player.years])
                        total_factor += table[player.years]
                        continue
                    for (low, high),values in table.items():

                        if low <= player.performance[factor] <= high:
                            if(debug):
                                print(factor, values[player.years])
                            total_factor += values[player.years]
                except KeyError as ke:
                    print("lookup failed")
                    pass

    """ 'escalator' format: 
    (18,22):{
            "BASE":{       2:0.03,  3:0.04,     4:0.05,     5:0.05 },
            "GP":{
                (0,179):{  2:0,     3:0,        4:0.01,     5:0.0125 },
                (180,1e4):{2:0.01,  3:0.0125,   4:0.015,    5:0.0175}
            },
            "MIN-PER-GAME":{
                (0,13)  :{ 2:0,     3:0,        4:0,        5:0},
                (12,15) :{ 2:0.005, 3:0.005,    4:0.005,    5:0.005},
                (16,18) :{ 2:0.0075,3:0.0075,   4:0.0075,   5:0.0075},
                (18,1e3):{ 2:0.01,  3:0.0125,   4:0.015,    5:0.0175}
            }
    },
    """

    return 1 + total_factor

class Player:

    def __init__(self, attr, performance, age=18, years=1, position="goalie"):

        self.isGoalie = True if position == "goalie" else False
        self.position = position # [center, wing, defense, goalie]
        self.age = age
        self.years = years
        self.performance = performance
        """ performance categories and factors for base player:
                gp              :  3000
                age (noted as G in tables?)
                    <20         :  5000
                    21-30       :  9000
                    31-45       : 12000
                    45+         : 15000
                points (noted as PTS)
                    <50         :  5000
                    50+         :  8000
                plus_minus      :  7500(as noted in table. Idk what it means)
                min_per_game    :  8000
                pim             : -1000
                ppg             : 20000
                shg             : 20000
                gwg             : 30000
                shots           :  1000
                indiv_rewards   : 75000
                team_playoffs   : 20000
                top_score    
                    1-5         :400000
                    6-10        :200000
                    11-15       :125000

                fo%             :  4000 (center only)
                shots_blocked   :  1000 (defense only)
                takeaways       :  1000 (defense only)
            
            performance categories for goalie:
                gp              : 4000
                starts          : 4000
                wins            : 5000
                sv pct          : 500
                gaa             : 100000
                so              : 15000
                saves           : 300
                win%            : 4000
                awards          : 75000
                playoffs        : 25000
                top 5sv pct     : 300000
                top 10 sv pct   : 150000
        """
        self.attributes = attr


def main():

    # { "attr": { (low, high):value, (low, high):value, ... } }

    player_value_ranges = {

        "build":{
            (238, 1e3):  500000,
            (225, 237):  450000,
            (213, 224):  335000,
            (200, 212):  225000,
            (188, 199):  115000,
            (176, 187):   70000,
            (163, 175):   50000,
            (  0, 162):   35000
        },
        "movement":{
            (189, 1e3):  500000,
            (179, 188):  450000,
            (169, 178):  335000,
            (159, 168):  225000,
            (149, 158):  115000,
            (139, 148):   70000,
            (129, 138):   50000,
            (  0, 128):   35000
        },
        "defense":{
            (284, 1e3): 1000000,
            (269, 283):  900000,
            (254, 268):  675000,
            (239, 253):  450000,
            (224, 238):  225000,
            (209, 223):  125000,
            (194, 208):   90000,
            (  0, 193):   60000
        },
        "offense":{
            (284, 1e3): 1525000,
            (269, 283): 1350000,
            (254, 268): 1000000,
            (239, 253):  675000,
            (224, 238):  340000,
            (209, 223):  225000,
            (194, 208):  150000,
            (  0, 193):   85000
        },
        "potential":{
            (229, 1e3):  525000,
            (215, 228):  450000,
            (200, 214):  350000,
            (185, 199):  225000,
            (170, 184):  112000,
            (155, 168):   68000,
            (145, 154):   45000,
            (  0, 144):   29000
        }

    }

    goalie_value_ranges = {

        "build":{
            (227, 1e3): 750000,
            (206, 226): 550000,
            (186, 205): 415000,
            (166, 185): 375000,
            (146, 165): 237500,
            (126, 145): 105000,
            (  0, 125):  95000
        },
        "movement":{
            (227, 1e3): 750000,
            (206, 226): 550000,
            (186, 205): 415000,
            (166, 185): 375000,
            (146, 165): 237500,
            (126, 145): 105000,
            (  0, 125):  95000
        },
        "control":{
            (185, 1e3): 750000,
            (179, 184): 550000,
            (169, 178): 415000,
            (159, 168): 375000,
            (149, 158): 237500,
            (139, 148): 105000,
            (  0, 138):  95000
        },
        "reaction":{
            (234, 1e3): 750000,
            (214, 233): 550000,
            (199, 213): 415000,
            (184, 198): 375000,
            (169, 183): 237500,
            (154, 168): 105000,
            (  0, 153):  95000
        },
        "potential":{
            (219, 1e3): 750000,
            (204, 218): 550000,
            (190, 203): 415000,
            (175, 189): 375000,
            (160, 174): 237500,
            (145, 159): 105000,
            (  0, 144):  95000
        }

    }

    player_performance_factors = {
        "GP"            :3000,
        "G<20"          :5000,
        "G21-30"        :9000,
        "G31-45"        :12000,
        "G45+"          :15000,
        "PTS<50"        :5000,
        "PTS50+"        :8000,
        "PLUS-MINUS"    :7500,
        "MIN-PER-GAME"  :8000,
        "PIM"           :-1000,
        "PPG"           : 20000,
        "SHG"           : 20000,
        "GWG"           : 30000,
        "SHOTS"         :  1000,
        "INDIV-REWARDS" : 75000,
        "TEAM-PLAYOFFS" : 20000,
        "TS1-5"         :400000,
        "TS6-10"        :200000,
        "TS11-15"       :125000,
        "FO%"           :4000, # Ctr only
        "SHOTS-BLOCKED" :1000, # Def only
        "TAKEAWAYS"       :1000  # Def only
    }
    goalie_performance_factors = {
        "GP"            : 4000,
        "STARTS"        : 4000,
        "WINS"          : 5000,
        "SVPCT"         : 500,
        "GAA"           : 100000,
        "SO"            : 15000,
        "SAVES"         : 300,
        "WIN%"          : 4000,
        "AWARDS"        : 75000,
        "PLAYOFFS"      : 25000,
        "TOP5SVPCT"     : 300000,
        "TOP10SVPCT"    : 150000
    }


    conduct_testing( player_value_ranges, goalie_value_ranges, player_performance_factors, goalie_performance_factors)


def conduct_testing( player_attr_brackets, goalie_attr_brackets, player_performance_factors, goalie_performance_factors ):

    player_attributes = {   "build":    215,
                            "movement": 170,
                            "defense":  255,
                            "offense":  255,
                            "potential":205}

    goalie_attributes = {   "build":    215,
                            "movement": 170,
                            "control":  255,
                            "reaction": 255,
                            "potential":205
                        }

    center_player_performance = {"GP"           : 80,
                                "G<20"          : 20,
                                "G21-30"        :  3,
                                "G31-45"        :  0,
                                "G45+"          :  0,
                                "PTS<50"        : 50,
                                "PTS50+"        : 15,
                                "PLUS-MINUS"    :-21,
                                "MIN-PER-GAME"  : 22,
                                "PIM"           : 79,
                                "PPG"           :  7,
                                "SHG"           :  0,
                                "GWG"           :  4,
                                "SHOTS"         :302,
                                "INDIV-REWARDS" :  0,
                                "TEAM-PLAYOFFS" :  0,
                                "TS1-5"         :  0,
                                "TS6-10"        :  0,
                                "TS11-15"       :  0,
                                "FO%"           :  0} # center only

    wing_player_performance = { "GP"            :80,
                                "G<20"          : 8,
                                "G21-30"        : 0,
                                "G31-45"        : 0,
                                "G45+"          : 0,
                                "PTS<50"        :27,
                                "PTS50+"        : 0,
                                "PLUS-MINUS"    : 4,
                                "MIN-PER-GAME"  : 9,
                                "PIM"           :12,
                                "PPG"           : 2,
                                "SHG"           : 0,
                                "GWG"           : 0,
                                "SHOTS"         :91,
                                "INDIV-REWARDS" : 0,
                                "TEAM-PLAYOFFS" : 0,
                                "TS1-5"         : 0,
                                "TS6-10"        : 0,
                                "TS11-15"       : 0
                                }

    defense_player_performance = {"GP"           : 76,
                                "G<20"          : 20,
                                "G21-30"        : 10,
                                "G31-45"        :  0,
                                "G45+"          :  0,
                                "PTS<50"        : 89,
                                "PTS50+"        :  0,
                                "PLUS-MINUS"    :  8,
                                "MIN-PER-GAME"  : 19,
                                "PIM"           : 62,
                                "PPG"           :  5,
                                "SHG"           :  1,
                                "GWG"           :  1,
                                "SHOTS"         :104,
                                "SHOTS-BLOCKED" : 85, # def only
                                "TAKEAWAYS"     :  3, # def only
                                "INDIV-REWARDS" :  0,
                                "TEAM-PLAYOFFS" :  0,
                                "TS1-5"         :  0,
                                "TS6-10"        :  0,
                                "TS11-15"       :  0}

    goalie_performance = {  "GP"        :   56,
                            "STARTS"    :   53,
                            "WINS"      :   25,
                            "SVPCT"     :  907,
                            "GAA"       :    3.05,
                            "SO"        :    0,
                            "SAVES"     : 1666,
                            "WIN%"      :   47,
                            "AWARDS"    :    0,
                            "PLAYOFFS"  :    1,
                            "TOP5SVPCT" :    0,
                            "TOP10SVPCT":    0}

    player_escalator = {
        (18,22):{
            "BASE":{       2:0.03,  3:0.04,     4:0.05,     5:0.05 },
            "GP":{
                (0,179):{  2:0,     3:0,        4:0.01,     5:0.0125 },
                (180,1e4):{2:0.01,  3:0.0125,   4:0.015,    5:0.0175}
            },
            "MIN-PER-GAME":{
                (0,11)  :{ 2:0,     3:0,        4:0,        5:0},
                (12,15) :{ 2:0.005, 3:0.005,    4:0.005,    5:0.005},
                (16,18) :{ 2:0.0075,3:0.0075,   4:0.0075,   5:0.0075},
                (18,1e3):{ 2:0.01,  3:0.0125,   4:0.015,    5:0.0175}
            }
        },
        (23,25):{
            "BASE":{        2:0.04,     3:0.05},
            "GP":{
                (0,199):{   2:-0.01,    3:-0.02 },
                (200,399):{ 2: 0.01,    3:0.0125},
                (400,1e4):{ 2: 0.015,   3:0.02  },
            },
            "MIN-PER-GAME":{
                (0,11)  : { 2:0,        3:0,    },
                (12,15) : { 2:0.005,    3:0.005 },
                (16,18) : { 2:0.0075,   3:0.01  },
                (18,1e3): { 2:0.015,    3:0.0175}
            }
        },
        (26,31):{
            "BASE":{
                2:0.05,
                3:0.055,
                4:0.06,
                5:0.065
            },
            "GP":{
                (0,179):  { 2:-0.01,    3:-0.01,    4:-0.01,     5:-0.01  },
                (180,299):{ 2: 0.01,    3: 0.0125,  4:0.015,    5: 0.0175},
                (300,1e4):{ 2: 0.015,   3: 0.0175,  4:0.02,     5: 0.0225}
            },
            "MIN-PER-GAME":{
                (0,11):   { 2:-0.005,   3:-0.01,    4:-0.015,   5:-0.025 },
                (12,15):  { 2: 0.0075,  3: 0.0075,  4: 0.0075,  5: 0.0075},
                (16,18):  { 2: 0.01,    3: 0.0125,   4: 0.015,   5: 0.0175},
                (18,1e3): { 2: 0.015,   3: 0.0175,   4: 0.02,    5: 0.0225}
            }
        },
        (32,1e3):{
            "BASE":{ 2:0.04, 3:0.045, 4:0.05, 5:0.055 },
            "GP":{
                (0,179):  { 2:-0.02,   3:-0.02,    4:-0.02,   5:-0.02},
                (180,799):{ 2: 0.01,   3: 0.0125,  4: 0.015,  5: 0.0175},
                (800,1e4):{ 2: 0.02,   3: 0.025,   4: 0.03,   5: 0.035}
            },
            "MIN-PER-GAME":{
                (0,11):   { 2:-0.02,   3:-0.025,    4:-0.03,    5:-0.035 },
                (12,15):  { 2: 0.005,  3: 0.005,    4: 0.005,   5: 0.005},
                (16,18):  { 2: 0.0075, 3: 0.0075,   4: 0.0075,  5: 0.0075},
                (18,1e3): { 2: 0.01,   3: 0.0125,   4: 0.015,   5: 0.0175}
            }
        },
        
          
    } 

    defense_escalator = {
        (18,22):{
            "BASE":{       2:0.03,  3:0.04,     4:0.05,     5:0.05 },
            "GP":{
                (0,179):{  2:0,     3:0,        4:0,        5:0 },
                (180,1e4):{2:0.01,  3:0.01,     4:0.01,     5:0.01}
            },
            "MIN-PER-GAME":{
                (0,13)  :{ 2:0,     3:0,        4:0,        5:0},
                (14,15) :{ 2:0.005, 3:0.005,    4:0.005,    5:0.005},
                (16,18) :{ 2:0.0075,3:0.0075,   4:0.0075,   5:0.0075},
                (19,1e3):{ 2:0.0125,3:0.015,    4:0.0175,   5:0.02}
            }
        },
        (23,25):{
            "BASE":{        2:0.04,     3:0.05},
            "GP":{
                (0,199):{   2:-0.01,    3:-0.02 },
                (200,399):{ 2: 0.01,    3:0.0125},
                (400,1e4):{ 2: 0.015,   3:0.02  },
            },
            "MIN-PER-GAME":{
                (0,11)  : { 2:0,        3:0,    },
                (12,15) : { 2:0.005,    3:0.005 },
                (16,18) : { 2:0.0075,   3:0.01  },
                (18,1e3): { 2:0.015,    3:0.0175}
            }
        },
        (26,30):{
            "BASE":{
                2:0.05,
                3:0.055,
                4:0.06,
                5:0.065
            },
            "GP":{
                (0,179):  { 2:-0.01,    3:-0.01,    4:0.01,     5:-0.01  },
                (180,299):{ 2: 0.01,    3: 0.015,   4:0.02,     5: 0.025},
                (300,1e4):{ 2: 0.0,     3: 0.0,     4:0.0,      5: 0.0}
            },
            "MIN-PER-GAME":{
                (0,11):   { 2: 0.005,   3: 0.0075,  4: 0.01,    5: 0.0125 },
                (12,15):  { 2: 0.0075,  3: 0.01,    4: 0.0125,  5: 0.015},
                (16,18):  { 2: 0.0125,  3: 0.015,   4: 0.0175,  5: 0.02},
                (18,1e3): { 2: 0.015,   3: 0.0175,  4: 0.02,    5: 0.0225}
            }
        },
        (31,1e3):{
            "BASE":{ 2:0.05, 3:0.05, 4:0.05, 5:0.05 },
            "GP":{
                (0,300):{  2:-0.02, 3:-0.02,4:-0.02,    5:-0.02},
                (300,1e4):{2:0,     3:0,    4:0,        5:0}
            },
            "MIN-PER-GAME":{
                (0,11):   { 2: 0   ,   3: 0,        4: 0,       5: 0 },
                (12,15):  { 2: 0.05,   3: 0.05,     4: 0.05,    5: 0.05},
                (16,18):  { 2: 0.0075, 3: 0.0075,   4: 0.0075,  5: 0.0075},
                (19,1e3): { 2: 0.0125, 3: 0.015,   4: 0.0175,   5: 0.02}
            }
        },
        
          
    }


    goalie_escalator = {
        (21,23):{
            "BASE":{       2:0.03,      3:0.04,     4:0.05,     5:0.06 },
            "GP":{
                (0,119):{  2:0,         3:0,        4:0,        5:0 },
                (120,1e3):{2:0.005,     3:0.005,    4:0.005,    5:0.005}
            },
            "STARTS":{
                (0,40)  :{  2:0.0025,   3:0.0025,   4:0.0025,   5:0.0025},
                (41,60) :{  2:0.005,    3:0.005,    4:0.005,    5:0.005}
            }
        },
        (24,29):{
            "BASE":{        2:0.05,     3:0.06,     4:0.07,     5:0.07 },
            "GP":{
                (0,199):{   2:0,        3:0,        4:0,        5:0    },
                (200,1e4):{ 2:0.005,    3:0.005,    4:0.005,    5:0.005},
            },
            "STARTS":{
                (0,11)  : { 2:0.0025,   3:0.0025,    4:0.0025,  5:0.0025},
                (12,15) : { 2:0.005,    3:0.0075,    4:0.01,    5:0.015 }
            }
        },
        (30,31):{
            "BASE":{        2:0.05,      3:0.05,     4:0.05,     5:0.05 },
            "GP":{
                (0,119):  { 2:-0.01,    3:-0.01,    4:-0.01,     5:-0.01  },
                (120,239):{ 2: 0.01,    3: 0.015,   4:0.02,     5: 0.025},
                (240,1e4):{ 2: 0.0,     3: 0.0,     4:0.0,      5: 0.0}
            },
            "STARTS":{
                (0,11):   { 2: 0.005,   3: 0.0075,  4: 0.01,    5: 0.0125 },
                (12,15):  { 2: 0.0075,  3: 0.01,    4: 0.0125,  5: 0.015}
            }
        },
        (32,1e3):{
            "BASE":{ 2:0.05, 3:0.05, 4:0.05, 5:0.05 },
            "GP":{
                (0,300):{  2:-0.02, 3:-0.02,4:-0.02,    5:-0.02},
                (300,1e4):{2:0,     3:0,    4:0,        5:0}
            },
            "STARTS":{
                (0,40):   { 2: 0   ,   3: 0,        4: 0,       5: 0 },
                (41,60):  { 2: 0.05,   3: 0.05,     4: 0.05,    5: 0.05}
            }
        },
        
          
    } 


    # setup

    tpc = Player(player_attributes, center_player_performance,  age=18, years=2,position="center")
    tpw = Player(player_attributes, wing_player_performance,    age=18, years=3,position="wing")
    tpd = Player(player_attributes, defense_player_performance, age=18, years=2,position="defense")

    tpg = Player(goalie_attributes, goalie_performance,         age=21, years=2,position="goalie")

    players = {"center":tpc,"wing":tpw,"defense":tpd,"goalie":tpg}

    ### Player contract testing ###

    print("\nPLAYER TESTING")

    for name, player in players.items():

        p_contract, perf_bonus, p_escalator = 0,0,0

        if player.isGoalie:
            p_contract  =   contract(goalie_attr_brackets, player )
            perf_bonus  =   performance_bonus(goalie_performance_factors, player, player.isGoalie )
        else:
            p_contract =    contract(player_attr_brackets, player )
            perf_bonus =    performance_bonus(player_performance_factors, player )
        
        if player.position == "defense":
            p_escalator = escalator(defense_escalator, player)
        elif player.position == "goalie":
            p_escalator = escalator(goalie_escalator, player)
        else:
            p_escalator = escalator(player_escalator, player, False)



        total = (p_contract+perf_bonus) * (p_escalator)

        print("{0} ({1}+{2})*{3} = ${4}".format(name, p_contract, perf_bonus, p_escalator, total ))




    """# GOALIE TESTING
                print("\nGOALIE TESTING")
                
                # contract
                tpg_contract = (contract(goalie_attr_brackets, tpg, goalie=True, debug=True ))
                
                ### Performance Bonus function testing ###
                tpg_perf_bonus = performance_bonus(goalie_performance_factors, tpg, goalie=True, debug=True)
                print("goalie:",tpg_perf_bonus, "correct? ",(tpg_perf_bonus == 1922300))
            """



if __name__ == '__main__':
    main()