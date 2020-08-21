<!DOCTYPE html>
<html>
    <head>
        <title>Custom Commands</title>
        <meta charset="utf-8">
        <link rel="icon" href="assets/cojiro.png" type="image/png">
        <link rel="stylesheet" href="css/base.css" type="text/css">
        <link rel="stylesheet" href="css/commands.css" type="text/css">
    </head>
    <body>
        <header>
            <h1>Discord Custom Commands</h1>
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
