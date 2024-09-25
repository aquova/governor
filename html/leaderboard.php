<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Leaderboard</title>
        <meta charset="utf-8">
        <link rel="icon" href="assets/cojiro.png" type="image/png">
        <link rel="stylesheet" href="css/base.css" type="text/css">
        <link rel="stylesheet" href="css/leaderboard.css" type="text/css">
        <link rel="stylesheet" href="css/tabs.css" type="text/css">

        <meta property="og:title" content="Stardew Valley Discord Leaderboard" />
        <meta property="og:url" content="https://stardew.chat/leaderboard.php" />
        <meta property="og:image" content="assets/cojiro.png" />
        <meta property="og:description" content="View the most active members of the Stardew Valley Discord server" />
    </head>
    <body>
        <header>
            <h1>Stardew Valley Discord Leaderboard</h1>
        </header>
        <main>
            <?php
                include 'db.php';
            ?>
            <div class="tab">
                <button class="tabbtn" id="monthlybtn" onclick="opentab(event, 'monthly')">This Month</button>
                <button class="tabbtn" id="alltimebtn" onclick="opentab(event, 'alltime')">All-Time</button>
            </div>
            <div id="monthly" class="tabcontent">
                <ul>
                    <?php
                        populate_leaderboard(true);
                    ?>
                </ul>
            </div>
            <div id="alltime" class="tabcontent">
                <ul>
                    <?php
                        populate_leaderboard(false);
                    ?>
                </ul>
            </div>
        </main>
    </body>
    <script src="js/tabs.js"></script>
</html>
