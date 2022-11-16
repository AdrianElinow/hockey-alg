
Implementations originally by Adrian Elinow for ltlhl.com (2022)

Comments included directly in source-code have also been sent as a more readable markdown file for future-documentation at client request

<?php
    
    function lthl_contract($brackets, $player_attr){

        /* $brackets -> nested associative array (from json config file)
         *      structure (in json format):     
                    "attribute":[
                        {"low": 238, "high":1000, "value":  500000},
                    ],
                    "attribute":[...],
                    ...
        */

        /* $player_attr: associative array (from player data entry)
         *      structure (in php aa format):
                    $player_attr = [
                        "attribute" => value,
                        ...
         */

        /* $values has been implemented using an int. However in case one
         *      may wish to use an alternative heuristic rather than the 
         *      average of values, change $values to an associative array,
         *      replace '$values += ...' with: 
         *          '$values[$attr] = $bracket["value"];''
         *      and calculate the desired heuristic at the end.
         */
        $value = 0;

        /* Based on this Python3 double list comprehension:
         *
         *  values = [ val  for attr in player_attr.keys() 
         *      for (low, high), val in brackets[attr].items() 
         *      if low <= player_attr[attr] <= high ]
        */

        foreach($brackets as $attr => $rangeValuePairs){

            foreach($rangeValuePairs as $bracket){

                if( $player_attr[$attr] >= $bracket["low"] && $player_attr[$attr] <= $bracket["high"] )
                        $value += $bracket["value"];

            }
        }
        
        return ($value / count($brackets));

    };

    function lthl_performance_bonus( $performance_factors, $player_performance, $isgoalie ){

        /* $performance_factors -> associative array
                structure (json): 
                    {
                        "factor" : score,
                        ...
            
            $player_performance -> associative array
                structure (php):
                    $player_center_performance = [
                        "factor" => score,
                        ...
        
            $isgoalie -> boolean
                for the purpose of properly applying the special exception calculation
         */


        $bonuses = array();

        foreach( $player_performance as $factor => $score )
            $bonuses[$factor] = ($score * $performance_factors[$factor]);

        # special calculation exception
        if( $isgoalie )
            $bonuses["GAA"] = 500000 - $bonuses["GAA"];

        return array_sum($bonuses);

    }

    function lthl_escalator( $escalator, $player_performance, $player_age, $player_years ){

        /* $escalator ->  nested associative array (from json config file) 
                structure: 
                    {"low":18, "high":22, "lookup":{
                        "YEARS":[
                            {"low":  0,"high":1000, "lookup":{  "2": 0.03,      "3":0.04,       "4":0.05,       "5":0.05}}
                        ],
                        "attr":[
                            {"low":  0,"high": 179, "lookup":{  "2": 0.00,      "3":0.00,       "4":0.01,       "5":0.0125}},
                            ...
                        ],
                        ...

            $player_performance -> associative array
                structure (php):
                    $player_center_performance = [
                        "factor" => score,
                        ...

            $player_age   -> integer
            $player_years -> integer
        */


        $total = 0;

        /* To properly determine which age bracket and entry value is correct for 
                a player, both the $player_age and $age_bracket[...] must be the same type
            In the json files, the keys to each 'lookup' entry must be strings,
                which means either they must be converted to integers or the 
                given player_age / player_years values must be converted to strings
            For efficiency, I have opted to convert the player values to strings:
         */
        $player_age = strval($player_age);

        /* $player_performance does not normally contain a "YEARS" entry,
                but for algorithmic simplicity, it is added because 
                there is an accompanying json entry for that field.
         */
        $player_performance["YEARS"] = strval($player_years);


        # escalator traversal

        foreach($escalator as $agebracket){

            if( $player_age >= $agebracket["low"] && $player_age <= $agebracket["high"]){

                foreach($agebracket["lookup"] as $factor => $factorbrackets){

                    foreach($factorbrackets as $bracket){

                        if( $player_performance[$factor] >= $bracket["low"] && $player_performance[$factor] <= $bracket["high"] )
                            #echo "\t",$factor,$bracket["lookup"][$player_years],"\n";
                            $total += $bracket["lookup"][$player_years];
                    }
                }

            }

        }

        /* returning 1+$total instead of just $total
                because allows this usage of this function as such:
                    ... = (contract(...) + perf_bonus(...)) * escalator(...)
                instead of this awkward alternative:
                    ... = (contract(...) + perf_bonus(...)) * (1 + escalator(...))
         */

        return (1 + $total);

    }

    function calculate( $name, $player_attr, $player_performance, $isgoalie, $player_age, $player_years, $player_attr_brackets, $player_performance_factors, $player_escalator){

        // current config for testing purposes. Not included in prod version

        $contract = lthl_contract($player_attr_brackets, $player_attr);
        $perf_bonus = lthl_performance_bonus($player_performance_factors, $player_performance, $isgoalie);
        $escalator = lthl_escalator($player_escalator, $player_performance, $player_age, $player_years);
        $total = ($contract + $perf_bonus) * $escalator;

        echo $name,': (',($contract),'+',($perf_bonus),')*',($escalator)," = $",($total),"\n";

        return $total;

    }

    # config file imports
    #    Not included in prod version. Service will automatically feed files as arguments
    $player_attr_brackets =         json_decode(file_get_contents("player_attributes_bracket.json"), TRUE);
    $goalie_attr_brackets =         json_decode(file_get_contents("goalie_attributes_bracket.json"), TRUE);
    
    $player_performance_factors =   json_decode(file_get_contents("player_performance_factors.json"), TRUE);
    $goalie_performance_factors =   json_decode(file_get_contents("goalie_performance_factors.json"), TRUE);
    
    $player_escalator =             json_decode(file_get_contents("player_escalator.json"), TRUE);
    $player_defense_escalator =     json_decode(file_get_contents("player_defense_escalator.json"), TRUE);
    $goalie_escalator =             json_decode(file_get_contents("goalie_escalator.json"), TRUE);


    # define testing structures
    #   representations of discrete database sample types to demonstrate functionality and accuracy.    
    $player_attr = [
        "build"     => 215,
        "movement"  => 170,
        "defense"   => 255,
        "offense"   => 255,
        "potential" => 205
    ];

    $goalie_attr = [
        "build"     => 215,
        "movement"  => 170,
        "control"   => 255,
        "reaction"  => 255,
        "potential" => 205
    ];

    $player_center_performance = [
        "GP"            => 80,
        "G<20"          => 20,
        "G21-30"        =>  3,
        "G31-45"        =>  0,
        "G45+"          =>  0,
        "PTS<50"        => 50,
        "PTS50+"        => 15,
        "PLUS-MINUS"    =>-21,
        "MIN-PER-GAME"  => 22,
        "PIM"           => 79,
        "PPG"           =>  7,
        "SHG"           =>  0,
        "GWG"           =>  4,
        "SHOTS"         =>302,
        "INDIV-REWARDS" =>  0,
        "TEAM-PLAYOFFS" =>  0,
        "TS1-5"         =>  0,
        "TS6-10"        =>  0,
        "TS11-15"       =>  0,
        "FO%"           =>  0
    ];

    $player_wing_performance = [
        "GP"            => 80,
        "G<20"          =>  8,
        "G21-30"        =>  0,
        "G31-45"        =>  0,
        "G45+"          =>  0,
        "PTS<50"        => 27,
        "PTS50+"        =>  0,
        "PLUS-MINUS"    =>  4,
        "MIN-PER-GAME"  =>  9,
        "PIM"           => 12,
        "PPG"           =>  2,
        "SHG"           =>  0,
        "GWG"           =>  0,
        "SHOTS"         => 91,
        "INDIV-REWARDS" =>  0,
        "TEAM-PLAYOFFS" =>  0,
        "TS1-5"         =>  0,
        "TS6-10"        =>  0,
        "TS11-15"       =>  0
    ];

    $player_defense_performance = [
        "GP"            => 76,
        "G<20"          => 20,
        "G21-30"        => 10,
        "G31-45"        =>  0,
        "G45+"          =>  0,
        "PTS<50"        => 89,
        "PTS50+"        =>  0,
        "PLUS-MINUS"    =>  8,
        "MIN-PER-GAME"  => 19,
        "PIM"           => 62,
        "PPG"           =>  5,
        "SHG"           =>  1,
        "GWG"           =>  1,
        "SHOTS"         =>104,
        "SHOTS-BLOCKED" => 85, # def only
        "TAKEAWAYS"     =>  3, 
        "INDIV-REWARDS" =>  0,
        "TEAM-PLAYOFFS" =>  0,
        "TS1-5"         =>  0,
        "TS6-10"        =>  0,
        "TS11-15"       =>  0
    ];

    $goalie_performance = [
        "GP"            =>   56,
        "STARTS"        =>   53,
        "WINS"          =>   25,
        "SVPCT"         =>  907,
        "GAA"           =>    3.05,
        "SO"            =>    0,
        "SAVES"         => 1666,
        "WIN%"          =>   47,
        "AWARDS"        =>    0,
        "PLAYOFFS"      =>    1,
        "TOP5SVPCT"     =>    0,
        "TOP10SVPCT"    =>    0
    ];


    # conduct testing to terminal

    echo "Calculations:\n";

    calculate( "Center",    $player_attr, $player_center_performance,   FALSE, 18, 2, $player_attr_brackets, $player_performance_factors, $player_escalator);
    calculate( "Wing",      $player_attr, $player_wing_performance,     FALSE, 18, 3, $player_attr_brackets, $player_performance_factors, $player_escalator);
    calculate( "Defense",   $player_attr, $player_defense_performance,  FALSE, 18, 2, $player_attr_brackets, $player_performance_factors, $player_defense_escalator);

    calculate( "Goalie",    $goalie_attr, $goalie_performance,          TRUE,  21, 2, $goalie_attr_brackets, $goalie_performance_factors, $goalie_escalator);

    # cross-compare values with python implementation and excel outputs
    #   or just use *nix built-in 'diff' functionality


?>

