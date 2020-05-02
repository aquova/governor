<!DOCTYPE html>
<html>
    <head>
        <title>Custom Commands</title>
        <meta charset="utf-8">
        <link rel="icon" href="cojiro.png" type="image/png">
        <link rel="stylesheet" href="css/base.css" type="text/css">

        <style>
            img {
                max-width: 300px;
                max-height: 300px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1></h1>
        </header>
        <main>
            <table>
                <tr>
                    <th>Command</th>
                    <th>Response</th>
                </tr>
                <?php
                    include 'db.php';
                    $populate_cmd_tbl();
                ?>
            </table>
        </main>
    </body>
</html>
