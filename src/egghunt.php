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
        <meta property="og:image" content="assets/SDV_Easter.png" />
    </head>
    <body>
        <header>
            <h1>Egg Hunt Leaderboard!</h1>
        </header>
        <main>
            <table>
                <?php
                    include 'db.php';
                    $populate_egghunt();
                ?>
            </table>
        </main>
    </body>
</html>
