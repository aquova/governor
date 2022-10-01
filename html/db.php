<?php
    // Constants
    define("DB_PATH", "/private/governor.db");
    define("XP_PER_LVL", 300);

    function populate_leaderboard($use_monthly) {
        $db = new SQLite3(DB_PATH);
        $query;
        if ($use_monthly) {
            $month = date('m');
            $year = date('Y');
            $query = $db->prepare('SELECT * FROM xp WHERE username IS NOT NULL AND monthly <> 0 AND month = ? AND year = ? ORDER BY monthly DESC LIMIT 100');
            $query->bindParam(1, $month, SQLITE3_INTEGER);
            $query->bindParam(2, $year, SQLITE3_INTEGER);
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
            $role_color = $row['color'];
            $avatar_img = $row['avatar'];

            $username = $row['username'];
            if ($username == "") {
                $username = "???";
            }

            echo "<li class='user'>";
            echo "<span class='user-rank'>$rank</span>";
            echo "<img class='user-img' src='$avatar_img'>";
            echo "<span class='user-name'>";
            echo "<span style='color:$role_color'>$username</span>";
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

            // Convert image URLs to img tags, other links to normal hyperlinks
            $url_regex = '/https?:\/\/\S+/';
            $found = preg_match_all($url_regex, $mes, $matches, PREG_OFFSET_CAPTURE);
            if ($found) {
                foreach ($matches[0] as $match) {
                    $url = $match[0];
                    $split = preg_split("/\./", $url);
                    $file_type = "";
                    if ($split) {
                        $file_type = end($split);
                    }

                    switch ($file_type) {
                        case "jpg":
                        case "png":
                            $mes = str_replace($url, "<img src=" . $url . ">", $mes);
                            break;

                        default:
                            $mes = str_replace($url, "<a href=" . $url . ">" . $url . "</a>", $mes);
                            break;
                    }
                }
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
