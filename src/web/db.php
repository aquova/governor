<?php
    class MyDB extends SQLite3 {
        function __construct($db_path) {
            $this->open($db_path);
        }
    }

    $config_file = "../private/config.json";
    $xp_per_lvl = 300;

    // Parse JSON file
    $raw_json = file_get_contents($config_file);
    $cfg = json_decode($raw_json, true);

    $db = new MyDB("../" . $cfg["db_path"]);
    if (!$db) {
        echo $db->lastErrorMsg();
    }

    $sql =<<< EOF
        SELECT * FROM xp ORDER BY xp DESC LIMIT 100;
    EOF;

    $ret = $db->query($sql);
    $rank = 0;
    while ($row = $ret->fetchArray(SQLITE3_ASSOC)) {
        $rank += 1;
        $id = $row['id'];
        $xp = $row['xp'] . "xp";
        $lvl = "Lvl " . floor($row['xp'] / $xp_per_lvl);

        $username = $row['username'];
        if ($row['avatar'] == "") {
            $avatar_img = "default_avatar.png";
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
?>
