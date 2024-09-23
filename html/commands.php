<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Custom Commands</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" href="assets/cojiro.png" type="image/png">
        <link rel="stylesheet" href="css/base.css" type="text/css">
        <link rel="stylesheet" href="css/commands.css" type="text/css">
        <script>
            function expandAll(expand) {
                for (const element of document.querySelectorAll("details"))
                    if (expand) {
                        element.setAttribute("open", "")
                    } else {
                        element.removeAttribute("open")
                    }
                }
        </script>
    </head>
    <body>
        <header>
            <h1>Discord Custom Commands</h1>
        </header>
        <main>
            <div class="center">
                <button onclick="expandAll(true)">Expand All</button>
                <button onclick="expandAll(false)">Compress All</button>
            </div>
            <br/>
            <?php
                include 'db.php';
                populate_cmd_tbl();
            ?>
        </main>
    </body>
</html>
