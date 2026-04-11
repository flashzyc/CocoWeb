<?php
declare(strict_types=1);

function db(): ?mysqli
{
    static $conn = null;
    if ($conn instanceof mysqli) {
        return $conn;
    }

    $host = (string) config('db_host');
    $port = (int) config('db_port');
    $user = (string) config('db_user');
    $pass = (string) config('db_pass');
    $db_name = (string) config('db_name');

    $conn = @new mysqli($host, $user, $pass, $db_name, $port);
    if ($conn->connect_errno) {
        if ($conn->connect_errno === 1049) {
            return null;
        }

        render_header('Database Error');
        echo '<div class="panel danger">';
        echo '<h2>Database connection failed</h2>';
        echo '<p>' . safe_text($conn->connect_error) . '</p>';
        echo '</div>';
        render_footer();
        exit;
    }

    $conn->set_charset('utf8mb4');
    return $conn;
}

function require_db(): mysqli
{
    $conn = db();
    if ($conn instanceof mysqli) {
        return $conn;
    }

    render_header('Setup Required');
    render_notice('Database not initialized. Run setup to create tables and seed data.', 'warn');
    echo '<div class="panel">';
    echo '<p>Open <strong>Setup</strong> and click <em>Initialize Database</em>.</p>';
    echo '<a class="button" href="setup.php">Go to Setup</a>';
    echo '</div>';
    render_footer();
    exit;
}
