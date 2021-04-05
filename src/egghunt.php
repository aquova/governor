<!DOCTYPE html>
<html>
    <head>
        <title>Egg Hunt!</title>
        <meta charset="utf-8">
        <link rel="icon" href="assets/cojiro.png" type="image/png">
        <link rel="stylesheet" href="css/base.css" type="text/css">
        <link rel="stylesheet" href="css/egghunt.css" type="text/css">

        <meta property="og:title" content="Egg Hunt Leaderboard" />
        <meta property="og:url" content="https://stardew.chat/egghunt.php" />
        <meta property="og:image" content="/assets/SDV_Easter.png" />
    </head>
    <body onresize="positionCrown()">
        <header>
            <h1>Egg Hunt Leaderboard!</h1>
        </header>
        <main>
            <img id='crown' src='assets/hunt_crown.png'>
            <table id='leader_tbl'>
                <?php
                    include 'db.php';
                    $populate_egghunt();
                ?>
            </table>
        </main>
    </body>
    <script>
        function positionCrown() {
            let tbl_x = document.getElementById('leader_tbl').getBoundingClientRect().left - 30
            document.getElementById('crown').style.left = tbl_x + "px"
        }
        positionCrown()
    </script>
</html>
