<?php
require_once __DIR__ . '/includes/bootstrap.php';

$conn = require_db();
$notice = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim($_POST['name'] ?? '');
    $message = trim($_POST['message'] ?? '');

    if ($name === '' || $message === '') {
        $notice = ['Message and name are required.', 'warn'];
    } else {
        $store_name = xss_store_input($name);
        $store_message = xss_store_input($message);
        $stmt = $conn->prepare("INSERT INTO guestbook (name, message) VALUES (?, ?)");
        if ($stmt) {
            $stmt->bind_param('ss', $store_name, $store_message);
            $stmt->execute();
            $stmt->close();
            $notice = ['Entry saved.', 'success'];
        } else {
            $notice = ['Insert failed: ' . $conn->error, 'error'];
        }
    }
}

$entries = $conn->query("SELECT id, name, message, created_at FROM guestbook ORDER BY id DESC LIMIT 10");

render_header('XSS Stored');
?>

<?php if ($notice): ?>
  <?php render_notice($notice[0], $notice[1]); ?>
<?php endif; ?>

<div class="panel">
  <form class="form" method="post" action="xss_stored.php">
    <div class="form-row">
      <label for="name">Name</label>
      <input id="name" name="name" type="text" placeholder="Your name">
    </div>
    <div class="form-row">
      <label for="message">Message</label>
      <textarea id="message" name="message" rows="4" placeholder="Leave a message"></textarea>
    </div>
    <button class="button" type="submit">Post</button>
  </form>
</div>

<div class="panel">
  <h3>Guestbook</h3>
  <div class="entries">
    <?php if ($entries && $entries->num_rows > 0): ?>
      <?php while ($row = $entries->fetch_assoc()): ?>
        <div class="entry">
          <div class="entry-head">
            <span class="entry-name"><?php echo xss_store_output($row['name']); ?></span>
            <span class="entry-time"><?php echo safe_text($row['created_at']); ?></span>
          </div>
          <div class="entry-body"><?php echo xss_store_output($row['message']); ?></div>
        </div>
      <?php endwhile; ?>
    <?php else: ?>
      <p class="muted">No entries yet.</p>
    <?php endif; ?>
  </div>
</div>

<?php render_footer(); ?>
