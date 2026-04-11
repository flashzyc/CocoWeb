<?php
require_once __DIR__ . '/includes/bootstrap.php';

$name = $_POST['name'] ?? '';
$output = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $output = xss_reflected_output($name);
}

render_header('XSS Reflected');
?>

<div class="panel">
  <form class="form" method="post" action="xss_reflected.php">
    <div class="form-row">
      <label for="name">Input</label>
      <input id="name" name="name" type="text" value="<?php echo safe_text($name); ?>" placeholder="Type something...">
    </div>
    <button class="button" type="submit">Send</button>
  </form>
</div>

<?php if ($output !== null): ?>
  <div class="panel">
    <h3>Response</h3>
    <div class="output">
      Hello, <?php echo $output; ?>
    </div>
  </div>
<?php endif; ?>

<div class="panel">
  <h3>Notes</h3>
  <p>The reflected output changes based on the selected security level.</p>
</div>

<?php render_footer(); ?>
