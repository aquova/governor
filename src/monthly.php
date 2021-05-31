<!DOCTYPE html>
<html>
    <head>
        <title>Leaderboard</title>
        <meta charset="utf-8">
        <link rel="icon" href="assets/cojiro.png" type="image/png">
        <link rel="stylesheet" href="css/base.css" type="text/css">
        <link rel="stylesheet" href="css/leaderboard.css" type="text/css">
        <link rel="stylesheet" href="css/ranks.css" type="text/css">

        <meta property="og:title" content="Stardew Valley Discord Montly Leaderboard" />
        <meta property="og:url" content="https://stardew.chat/monthly.php" />
        <meta property="og:image" content="assets/cojiro.png" />
        <meta property="og:description" content="View the most active members of the Stardew Valley Discord server this month" />
    </head>
    <body>
        <header>
            <h1>Stardew Valley Discord Monthly Leaderboard</h1>
        </header>
        <main>
            <ul>
            <?php
                include 'db.php';
                populate_leaderboard(true);
            ?>
            </ul>
        </main>
    </body>
</html>
