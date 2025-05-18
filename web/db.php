<?php
    // Constants
    define("DB_PATH", "/private/governor.db");
    define("XP_PER_LVL", 300);
    define("URL_REGEX", "/\b(https?:\/\/\S+)\b\/?/");
    define("LIMIT_FLAG", 2);

    enum LeaderboardType {
        case Total;
        case Monthly;
        case Weekly;
    }

    function get_month() {
        $year = date('Y');
        $month = date('m');
        // Needs to match get_month() in db.py
        return 12 * ($year - 2000) + $month - 1;
    }

    function get_week() {
        $year = date('Y');
        $week = date('W');
        // Needs to match get_week() in db.py
        return 52 * ($year - 2000) + $week;
    }

    function populate_leaderboard($type) {
        $db = new SQLite3(DB_PATH);
        $query;
        switch ($type) {
            case LeaderboardType::Weekly:
                $week = get_week();
                $query = $db->prepare('SELECT * FROM xp WHERE username IS NOT NULL AND weekly <> 0 AND week = ? ORDER BY weekly DESC LIMIT 100');
                $query->bindParam(1, $week, SQLITE3_INTEGER);
                break;
            case LeaderboardType::Monthly:
                $month = get_month();
                $query = $db->prepare('SELECT * FROM xp WHERE username IS NOT NULL AND monthly <> 0 AND month = ? ORDER BY monthly DESC LIMIT 100');
                $query->bindParam(1, $month, SQLITE3_INTEGER);
                break;
            case LeaderboardType::Total:
                $query = $db->prepare('SELECT * FROM xp WHERE username IS NOT NULL ORDER BY xp DESC LIMIT 100');
                break;
        }
        $ret = $query->execute();

        $rank = 0;
        while ($row = $ret->fetchArray()) {
            $rank += 1;
            $id = $row['id'];
            $xp = match($type) {
                LeaderboardType::Weekly => $row['weekly'] . "xp this week",
                LeaderboardType::Monthly => $row['monthly'] . "xp this month",
                LeaderboardType::Total => $row['xp'] . "xp"
            };
            $user_level = floor($row['xp'] / XP_PER_LVL);
            $lvl = "Lvl " . $user_level;
            $role_color = $row['color'];
            $avatar_img = $row['avatar'];
            // Single digit avatar images appear to be a randomly chosen default avatar, which don't resolve correctly
            // The avatar URLs follow the pattern of "https://cdn.discordapp.com/embed/avatar/<ID>?size=64", which is 50 characters. We'll check if the given URL is only slightly over that
            if (strlen($avatar_img) < 57) {
                $avatar_img = "assets/default_avatar.png";
            }

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
        $ret = $db->query('SELECT * FROM commands LEFT OUTER JOIN aliases ON commands.name = aliases.command ORDER BY commands.name');

        while ($row = $ret->fetchArray()) {
            $cmd = $row['name'];
            $title = $row['title'];
            $mes = $row['response'];
            $img = $row['img'];
            $flags = $row['flag'];
            $aliases = $row['alias'];

            if ($mes) {
                // Strip out any HTML tags, to prevent injection
                $mes = htmlspecialchars($mes);
                // We often use '<>' in the server to remove embeds, or '()' in the commands
                $mes = preg_replace("/&lt;(\S+)&gt;/", "$1", $mes);
                $mes = preg_replace("/\((\S+)\)/", "$1", $mes);
                // Convert URLs to hyperlinks
                $mes = preg_replace(URL_REGEX, "<a href=$1>$1</a>", $mes);
                // New lines should become html breaks
                $mes = str_replace("\n", "<br/>", $mes);
            }

            // Check if command has the limit flag set
            $limited = $flags & LIMIT_FLAG;

            echo "<details>";
            echo "<summary id=$cmd>$cmd</summary>";
            if ($title) {
                echo "<h2>$title</h2>";
            }
            if ($mes) {
                echo "<p>$mes</p>";
            }
            if ($img) {
                echo "<img src='$img'/>";
            }
            if ($aliases) {
                echo "<p>Aliases: $aliases</p>";
            }
            if ($limited) {
                echo "<p><small>This command is limited in some channels</small></p>";
            }
            echo "</details>";
            echo "<br/>";
        }
        $db->close();
    };
?>
