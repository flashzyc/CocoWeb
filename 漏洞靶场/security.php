<?php
require_once __DIR__ . '/includes/bootstrap.php';

$notice = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $level = $_POST['level'] ?? '';
    set_security_level($level);
    $notice = 'Security level updated.';
}

$current = security_level();
render_header('Security Level');
?>

<?php if ($notice): ?>
  <?php render_notice($notice, 'success'); ?>
<?php endif; ?>

<div class="panel">
  <form class="form" method="post" action="security.php">
    <div class="form-row">
      <label for="level">Choose security level</label>
      <select id="level" name="level">
        <?php foreach (SECURITY_LEVELS as $level): ?>
          <option value="<?php echo safe_text($level); ?>" <?php echo $level === $current ? 'selected' : ''; ?>>
            <?php echo safe_text(security_level_label($level)); ?>
          </option>
        <?php endforeach; ?>
      </select>
    </div>
    <button class="button" type="submit">Save</button>
  </form>
</div>

<div class="panel">
  <h3>What levels mean</h3>
  <ul class="feature-list">
    <li><strong>Low</strong>: intentionally vulnerable and unsafe.</li>
    <li><strong>Medium</strong>: naive filtering and basic checks.</li>
    <li><strong>High</strong>: safer patterns like prepared statements and output encoding.</li>
  </ul>
</div>

<?php render_footer(); ?>
