<?php
require_once __DIR__ . '/includes/bootstrap.php';

$conn = require_db();
$level = security_level();

$notice = $_SESSION['csrf_notice'] ?? null;
unset($_SESSION['csrf_notice']);

$token = '';
if ($level === 'medium') {
    $token = 'cocoweb_medium_token';
} elseif ($level === 'high') {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(16));
    }
    $token = $_SESSION['csrf_token'];
}

$users = $conn->query("SELECT id, username, email FROM users ORDER BY id ASC LIMIT 20");

render_header('CSRF');
?>

<?php if ($notice): ?>
  <?php render_notice($notice['message'], $notice['type']); ?>
<?php endif; ?>

<div class="split">
  <div class="panel">
    <h3>Update Email</h3>
    <form class="form" method="post" action="csrf_action.php">
      <div class="form-row">
        <label for="user_id">User</label>
        <select id="user_id" name="user_id">
          <?php if ($users && $users->num_rows > 0): ?>
            <?php $users->data_seek(0); ?>
            <?php while ($row = $users->fetch_assoc()): ?>
              <option value="<?php echo safe_text($row['id']); ?>">
                <?php echo safe_text($row['username']); ?> (<?php echo safe_text($row['email']); ?>)
              </option>
            <?php endwhile; ?>
          <?php else: ?>
            <option value="0">No users</option>
          <?php endif; ?>
        </select>
      </div>
      <div class="form-row">
        <label for="email">New Email</label>
        <input id="email" name="email" type="email" placeholder="user@example.local">
      </div>
      <?php if ($token !== ''): ?>
        <input type="hidden" name="token" value="<?php echo safe_text($token); ?>">
      <?php endif; ?>
      <button class="button" type="submit">Update</button>
    </form>
    <?php if ($level === 'medium'): ?>
      <p class="muted hint">Medium uses a static token: <code>cocoweb_medium_token</code></p>
    <?php elseif ($level === 'high'): ?>
      <p class="muted hint">High uses a per-session token.</p>
    <?php else: ?>
      <p class="muted hint">Low has no CSRF protection.</p>
    <?php endif; ?>
  </div>

  <div class="panel">
    <h3>Current Users</h3>
    <?php if ($users && $users->num_rows > 0): ?>
      <table class="table">
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Email</th>
        </tr>
        <?php $users->data_seek(0); ?>
        <?php while ($row = $users->fetch_assoc()): ?>
          <tr>
            <td><?php echo safe_text($row['id']); ?></td>
            <td><?php echo safe_text($row['username']); ?></td>
            <td><?php echo safe_text($row['email']); ?></td>
          </tr>
        <?php endwhile; ?>
      </table>
    <?php else: ?>
      <p class="muted">No users available. Import seed data in Setup.</p>
    <?php endif; ?>
  </div>
</div>

<div class="panel">
  <h3>Notes</h3>
  <ul class="feature-list">
    <li>Low: no token required.</li>
    <li>Medium: predictable token.</li>
    <li>High: session-bound token.</li>
  </ul>
</div>

<?php render_footer(); ?>
