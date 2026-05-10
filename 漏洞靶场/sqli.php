<?php
require_once __DIR__ . '/includes/bootstrap.php';

$conn = require_db();
$input = $_GET['id'] ?? '';
$rows = [];
$sql_note = null;
$error = null;

if (isset($_GET['search'])) {
    $level = security_level();
    if ($level === 'low') {
        // Security note: this branch intentionally concatenates user input into SQL
        // to demonstrate a classic SQL injection vulnerability in a training lab.
        $sql = "SELECT id, username, email FROM users WHERE id = '$input'";
        $sql_note = $sql;
        $result = $conn->query($sql);
    } elseif ($level === 'medium') {
        $safe = preg_replace('/[^0-9]/', '', $input);
        $sql = "SELECT id, username, email FROM users WHERE id = $safe";
        $sql_note = $sql;
        $result = $conn->query($sql);
    } else {
        // Security note: prepared statements with parameter binding are the
        // recommended mitigation for SQL injection in real applications.
        $sql_note = 'Prepared statement with parameter binding.';
        $stmt = $conn->prepare("SELECT id, username, email FROM users WHERE id = ?");
        if ($stmt) {
            $id = (int) $input;
            $stmt->bind_param('i', $id);
            $stmt->execute();
            $result = $stmt->get_result();
        } else {
            $result = false;
        }
    }

    if ($result === false) {
        $error = 'Query failed: ' . $conn->error;
    } else {
        while ($row = $result->fetch_assoc()) {
            $rows[] = $row;
        }
    }
}

render_header('SQL Injection');
?>

<?php if ($error): ?>
  <?php render_notice($error, 'error'); ?>
<?php endif; ?>

<div class="panel">
  <form class="form" method="get" action="sqli.php">
    <div class="form-row">
      <label for="id">User ID</label>
      <input id="id" name="id" type="text" value="<?php echo safe_text($input); ?>" placeholder="e.g. 1">
    </div>
    <button class="button" type="submit" name="search" value="1">Search</button>
  </form>
</div>

<?php if ($sql_note): ?>
  <div class="panel">
    <h3>Query</h3>
    <pre class="code"><?php echo safe_text($sql_note); ?></pre>
  </div>
<?php endif; ?>

<div class="panel">
  <h3>Results</h3>
  <?php if ($rows): ?>
    <table class="table">
      <tr>
        <th>ID</th>
        <th>Username</th>
        <th>Email</th>
      </tr>
      <?php foreach ($rows as $row): ?>
        <tr>
          <td><?php echo safe_text($row['id']); ?></td>
          <td><?php echo safe_text($row['username']); ?></td>
          <td><?php echo safe_text($row['email']); ?></td>
        </tr>
      <?php endforeach; ?>
    </table>
  <?php else: ?>
    <p class="muted">No results.</p>
  <?php endif; ?>
</div>

<?php render_footer(); ?>
