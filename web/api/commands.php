<?php
    define("DB_PATH", "/private/governor.db");

    header("Content-Type: application/json; charset=UTF-8");
    http_response_code(200);
    $db = new SQLite3(DB_PATH);
    $ret = $db->query('SELECT * FROM commands LEFT OUTER JOIN aliases ON commands.name = aliases.command ORDER BY commands.name');
    $data = array();
    while ($raw = $ret->fetchArray()) {
        $row = array(
            'name' => $raw['name'],
            'title' => $raw['title'] ? $raw['title'] : "",
            'response' => $raw['response'] ? $raw['response'] : "",
            'image' => $raw['img'] ? $raw['img'] : "",
            'flags' => $raw['flag'],
            'aliases' => $raw['alias'] ? array($raw['alias']) : [],
        );
        array_push($data, $row);
    }
    echo json_encode($data);
    $db->close();
?>
