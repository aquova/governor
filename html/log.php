<?php
header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

function get_string_between($string, $start, $end){
    $string = ' ' . $string;
    $ini = strpos($string, $start);
    if ($ini == 0) return '';
    $ini += strlen($start);
    $len = strpos($string, $end, $ini) - $ini;
    return substr($string, $ini, $len);
}

$credits = "Made by AnotherPillow, base PHP code by xintrix (xintrix-dev on github)";

$mc1 = get_string_between($link, '"log-message-text">', '</span>');

$files = glob('../images/*');
//$loglink = "https://smapi.io/log/1d07e685d20b4fa2be7907c9b4b3aeb3";
$loglink = $_SERVER["QUERY_STRING"];
$logid = ltrim($loglink,"https://smapi.io/log/");
$link = file_get_contents($loglink);

$sdv = get_string_between($link, 'data-game-version="', '"');
//set success to false if sdv is blank
if ($sdv == "") {
    $sdvsuccess = false;
} else {
    $sdvsuccess = true;
}

//$sv2 = str_replace(array('<td v-pre>'), '',$sv1);
//$sv3 = str_replace(array(' '), '',$sv2);
//$sdv = ltrim($sv1,"\r\n");

$smapi = get_string_between($link, 'data-smapi-version="', '"');

if ($smapi == "") {
    $smapisuccess = false;
} else {
    $smapisuccess = true;
}
//$sm2 = str_replace(array('<td v-pre>'), '',$sm1);
//$sm3 = str_replace(array(' '), '',$sm2);
//$smapi = ltrim($sm3,"\r\n");

$gamepath = get_string_between($link, 'data-game-path="', '"');
if ($gamepath == "") {
    $gamepathsuccess = false;
} else {
    $gamepathsuccess = true;
}


$os = get_string_between($link, 'data-os="', '"');
$smods = get_string_between($link, 'data-code-mods="', '"');
//$smods = (int)$smods - 2;
//$smods = (string)$smods;

$cpack = get_string_between($link, 'data-content-packs="', '"');

if ($cpack == "") {
    $cpacksuccess = false;
} else {
    $cpacksuccess = true;
}
if ($smods == "") {
    $smodssuccess = false;
} else {
    $smodssuccess = true;
}
if ($os == "") {
    $ossuccess = false;
} else {
    $ossuccess = true;
}

//if any of them is false, set success to false
if ($sdvsuccess == false || $smapisuccess == false || $gamepathsuccess == false || $ossuccess == false || $cpacksuccess == false || $smodssuccess == false) {
    $success = false;
} else {
    $success = true;
}

//$gp2 = str_replace(array('<td v-pre>'), '',$gp1);
//$gp3 = str_replace(array(' '), '',$gp2);
//$parsed4 = str_replace(array(''), '',$parsed3);
//$gamepath = ltrim($gp3,"\r\n");

//$querry = $_SERVER['QUERY_STRING']
//$parsestr = parse_str($_SERVER['QUERY_STRING'], $queries);
//$parsestr = $_SERVER["QUERY_STRING"];


//$data = ['image' => $image_path, 'link' => $link, 'loglink' => $loglink, 'logid' => $logid, 'gamepath' => $gamepath, 'query' => $loglink];
$data = ['StardewVersion' => $sdv, 'SMAPI_ver' => $smapi, 'SMAPIMods' => $smods, 'ContentPacks' => $cpack, 'OS' => $os, 'gamepath' => $gamepath, 'credits' => $credits, 'success' => $success];

echo json_encode($data);