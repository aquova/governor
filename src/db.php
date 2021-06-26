<?php
    // Constants
    define("DB_PATH", "../governor.db");
    define("XP_PER_LVL", 300);

    define("VILLAGER_LVL", 1);
    define("COWPOKE_LVL", 5);
    define("FARMER_LVL", 25);
    define("SHEPHERD_LVL", 100);
    define("RANCHER_LVL", 250);
    define("CROPMASTER_LVL", 500);
    define("DESPERADO_LVL", 1000);

    function get_role_class($lvl) {
        $role = "class='villager'";

        if ($lvl >= DESPERADO_LVL) {
            $role = "class='desperado'";
        } elseif ($lvl >= CROPMASTER_LVL) {
            $role = "class='cropmaster'";
        } elseif ($lvl >= RANCHER_LVL) {
            $role = "class='rancher'";
        } elseif ($lvl >= SHEPHERD_LVL) {
            $role = "class='shepherd'";
        } elseif ($lvl >= FARMER_LVL) {
            $role = "class='farmer'";
        } elseif ($lvl >= COWPOKE_LVL) {
            $role = "class='cowpoke'";
        }

        return $role;
    };

    function populate_leaderboard($use_monthly) {
        $db = new SQLite3(DB_PATH);
        $query;
        if ($use_monthly) {
            $month = date('m');
            $query = $db->prepare('SELECT * FROM xp WHERE username IS NOT NULL AND monthly <> 0 AND month = ? ORDER BY monthly DESC LIMIT 100');
            $query->bindParam(1, $month, SQLITE3_INTEGER);
        } else {
            $query = $db->prepare('SELECT * FROM xp WHERE username IS NOT NULL ORDER BY xp DESC LIMIT 100');
        }
        $ret = $query->execute();

        $rank = 0;
        while ($row = $ret->fetchArray()) {
            $rank += 1;
            $id = $row['id'];
            $xp = "";
            if ($use_monthly) {
                $xp = $row['monthly'] . "xp this month";
            } else {
                $xp = $row['xp'] . "xp";
            }
            $user_level = floor($row['xp'] / XP_PER_LVL);
            $lvl = "Lvl " . $user_level;
            $role_class = get_role_class($user_level);

            $username = $row['username'];
            if ($username == "") {
                $username = "???";
            }

            if ($row['avatar'] == "") {
                $avatar_img = "assets/default_avatar.png";
            } else {
                $avatar_img = "https://cdn.discordapp.com/avatars/" . $id . "/" . $row['avatar'] . ".png";
            }

            echo "<li class='user'>";
            echo "<span class='user-rank'>$rank</span>";
            echo "<img class='user-img' src='$avatar_img'>";
            echo "<span class='user-name'>";
            echo "<span $role_class>$username</span>";
            echo "<br>";
            echo "<span class='user-id'>$id</span>";
            echo "</span>";
            echo "<span class='user-lvl'>";
            echo "<span>$lvl</span>";
            echo "<br>";
            echo "<span class='user-xp'>$xp</span>";
            echo "</span>";
            echo "</li>";
        }

        $db->close();
    };

    function populate_cmd_tbl() {
        $db = new SQLite3(DB_PATH);
        $ret = $db->query('SELECT * FROM commands ORDER BY name');

        while ($row = $ret->fetchArray()) {
            $cmd = $row['name'];
            $mes = $row['response'];

            // For closer formatting to how they'll appear in Discord,
            // we shall replace some items with html tags

            // We often use '<>' in the server to remove embeds, or '()' in the commands
            // These mess up the regex later on, so just strip them out now.
            $mes = preg_replace("/<(\S+)>/", "$1", $mes);
            $mes = preg_replace("/\((\S+)\)/", "$1", $mes);

            // Remove ``` Discord markdown notes
            // TODO: Someday make these into <code> blocks
            $mes = str_replace("```", "", $mes);

            // Turn whitelisted images into img tags
            $img_regex = "/(https?:\/\/\S*(discordapp|imgur)\.(com|net)\S+)/";
            $mes = preg_replace($img_regex, "<img src=$1>", $mes);

            // Turn all other links into hyperlinks
            $url_regex = '/(https?:\/\/\S+)/';
            if ((preg_match($url_regex, $mes)) and !(preg_match($img_regex, $mes))) {
                $mes = preg_replace($url_regex, "<a href=$1>$1</a>", $mes);
            }

            // New lines should become html breaks
            $mes = str_replace("\n", "<br/>", $mes);

            echo "<tr>";
            echo "<td>$cmd</td>";
            echo "<td>$mes</td>";
            echo "</tr>";
        }

        $db->close();
    };

    function populate_egghunt() {
        $db = new SQLite3(DB_PATH);
        $ret = $db->query('SELECT * FROM hunters ORDER BY count DESC LIMIT 10');

        $rank = 0;
        while ($row = $ret->fetchArray()) {
            $rank += 1;
            $name = $row['username'];
            $cnt = $row['count'];

            echo "<tr>";
            echo "<td class='hunter-rank'>$rank</td>";
            echo "<td class='hunter-name'>$name</td>";
            echo "<td class='hunter-count'>$cnt</td>";
            echo "</tr>";
        }

        $db->close();
    };
?>
