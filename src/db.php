<?php
    $db_path = "../sdv_data.db";

    $populate_leaderboard = function () use ($db_path) {
        $xp_per_lvl = 300;

        $db = new SQLite3($db_path);
        $ret = $db->query('SELECT * FROM xp WHERE username IS NOT NULL ORDER BY xp DESC LIMIT 100');

        $rank = 0;
        while ($row = $ret->fetchArray()) {
            $rank += 1;
            $id = $row['id'];
            $xp = $row['xp'] . "xp";
            $lvl = "Lvl " . floor($row['xp'] / $xp_per_lvl);

            $username = $row['username'];
            if ($username == "") {
                $username = "???";
            }

            if ($row['avatar'] == "") {
                $avatar_img = "assets/default_avatar.png";
            } else {
                $avatar_img = "https://cdn.discordapp.com/avatars/" . $id . "/" . $row['avatar'] . ".png";
            }

            // TODO: Make this nicer
            echo "<li class='user'>";
            echo "<span class='user-rank'>$rank</span>";
            echo "<img class='user-img' src='$avatar_img'>";
            echo "<span class='user-name'>";
            echo "<span>$username</span>";
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

    $populate_cmd_tbl = function () use ($db_path) {

        $db = new SQLite3($db_path);
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
?>
