<?php
require_once __DIR__ . '/includes/bootstrap.php';

function db_admin_connect(): ?mysqli
{
    $host = (string) config('db_host');
    $port = (int) config('db_port');
    $user = (string) config('db_user');
    $pass = (string) config('db_pass');

    $conn = @new mysqli($host, $user, $pass, '', $port);
    if ($conn->connect_errno) {
        return null;
    }
    $conn->set_charset('utf8mb4');
    return $conn;
}

function mask_value(string $value): string
{
    if ($value === '') {
        return '(empty)';
    }
    return str_repeat('*', max(4, strlen($value)));
}

$sql_file = __DIR__ . '/seed.sql';

function run_sql_file(mysqli $conn, string $file_path, array &$actions, array &$errors): void
{
    if (!file_exists($file_path)) {
        $errors[] = 'SQL file not found.';
        return;
    }

    $lines = file($file_path, FILE_IGNORE_NEW_LINES);
    if ($lines === false) {
        $errors[] = 'Failed to read SQL file.';
        return;
    }

    $filtered = [];
    foreach ($lines as $line) {
        $trim = trim($line);
        if ($trim === '' || strpos($trim, '--') === 0 || strpos($trim, '#') === 0) {
            continue;
        }
        $filtered[] = $line;
    }

    $sql = implode("\n", $filtered);
    $statements = array_filter(array_map('trim', explode(';', $sql)));

    foreach ($statements as $statement) {
        if ($conn->query($statement)) {
            $actions[] = 'SQL executed.';
        } else {
            $errors[] = 'SQL error: ' . $conn->error;
        }
    }
}

$actions = [];
$errors = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['setup'])) {
    $admin = db_admin_connect();
    if (!$admin) {
        $errors[] = 'Failed to connect to MySQL. Check config.php and phpstudy MySQL status.';
    } else {
        $dbName = (string) config('db_name');
        $createDb = "CREATE DATABASE IF NOT EXISTS `$dbName` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci";
        if ($admin->query($createDb)) {
            $actions[] = 'Database created or already exists.';
        } else {
            $errors[] = 'Database create failed: ' . $admin->error;
        }

        $admin->close();
        $conn = db();
        if (!$conn) {
            $errors[] = 'Database not reachable after creation. Verify permissions.';
        } else {
            $schema = [
                "CREATE TABLE IF NOT EXISTS users (
                    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4",
                "CREATE TABLE IF NOT EXISTS guestbook (
                    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            ];

            foreach ($schema as $sql) {
                if ($conn->query($sql)) {
                    $actions[] = 'Table prepared.';
                } else {
                    $errors[] = 'Table create failed: ' . $conn->error;
                }
            }

        }
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['import'])) {
    $conn = db();
    if (!$conn) {
        $errors[] = 'Database not ready. Initialize database first.';
    } else {
        run_sql_file($conn, $sql_file, $actions, $errors);
    }
}

render_header('Setup');
?>

<?php if ($actions): ?>
  <?php foreach ($actions as $message): ?>
    <?php render_notice($message, 'success'); ?>
  <?php endforeach; ?>
<?php endif; ?>

<?php if ($errors): ?>
  <?php foreach ($errors as $message): ?>
    <?php render_notice($message, 'error'); ?>
  <?php endforeach; ?>
<?php endif; ?>

<div class="panel">
  <h3>Configuration</h3>
  <table class="table">
    <tr><th>Host</th><td><?php echo safe_text((string) config('db_host')); ?></td></tr>
    <tr><th>Port</th><td><?php echo safe_text((string) config('db_port')); ?></td></tr>
    <tr><th>User</th><td><?php echo safe_text((string) config('db_user')); ?></td></tr>
    <tr><th>Password</th><td><?php echo safe_text(mask_value((string) config('db_pass'))); ?></td></tr>
    <tr><th>Database</th><td><?php echo safe_text((string) config('db_name')); ?></td></tr>
  </table>
</div>

<div class="panel">
  <h3>Initialize Database</h3>
  <p>This creates the database and tables for the labs.</p>
  <form method="post" action="setup.php">
    <button class="button" type="submit" name="setup" value="1">Initialize Database</button>
  </form>
</div>

<div class="panel">
  <h3>Import Seed Data</h3>
  <p>Loads expanded sample data from <code>seed.sql</code>.</p>
  <form method="post" action="setup.php">
    <button class="button" type="submit" name="import" value="1">Import Seed Data</button>
  </form>
  <?php if (!file_exists($sql_file)): ?>
    <p class="muted">seed.sql not found.</p>
  <?php endif; ?>
</div>

<?php render_footer(); ?>
