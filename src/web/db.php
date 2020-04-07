<?php
    class MyDB extends SQLite3 {
        function __construct($db_path) {
            $this->open($db_path);
        }
    }

    // Parse JSON file
    $raw_json = file_get_contents("../private/config.json");
    $cfg = json_decode($raw_json, true);

    $db = new MyDB("../" . $cfg["db_path"]);
    if (!$db) {
        echo $db->lastErrorMsg();
    }

    $sql =<<< EOF
        SELECT * FROM xp ORDER BY xp DESC LIMIT 100;
    EOF;

    $ret = $db->query($sql);
    while ($row = $ret->fetchArray(SQLITE3_ASSOC)) {
        echo "<li class='user'>";
        $id = $row['id'];
        echo "<span>$id</span>";
        echo "</li>";
    }
    $db->close();
?>
