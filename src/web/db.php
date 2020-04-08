<?php
    class MyDB extends SQLite3 {
        function __construct($db_path) {
            $this->open($db_path);
        }
    }

    // TODO: Maybe make this a class, to reuse cUrl connection?
    function fetch_user($id, $token) {
        // Discord API URL
        $url = "https://discordapp.com/api/users/" . $id;

        $curl = curl_init($url);
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($curl, CURLOPT_HTTPHEADER, [
            "Authorization: Bot " . $token,
            "Content-Type: application/json"
        ]);

        $response = curl_exec($curl);
        curl_close($curl);

        return $response;
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
    $row = $ret->fetchArray(SQLITE3_ASSOC);
    $rank = 0;
    while ($row = $ret->fetchArray(SQLITE3_ASSOC)) {
        $rank += 1;
        // TEMP: Only do 20 for now
        if ($rank > 20) {
            break;
        }
        $id = $row['id'];
        $xp = $row['xp'] . "xp";
        $lvl = "Lvl " . floor($row['xp'] / $xp_per_lvl);

        $raw_user = fetch_user($id, $cfg["discord"]);
        $user_data = json_decode($raw_user, true);

        $avatar_img = "https://cdn.discordapp.com/avatars/" . $user_data['id'] . "/" . $user_data['avatar'] . ".png";
        $username = $user_data['username'] . "#" . $user_data['discriminator'];

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

        // Try sleeping briefly, to get around API rate limit
        sleep(0.1);
    }
    $db->close();
?>
