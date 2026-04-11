<?php
require_once __DIR__ . '/includes/bootstrap.php';

render_header('Dashboard');
?>
<section class="grid">
  <div class="panel">
    <h2>Welcome</h2>
    <p>CocoWeb is a local vulnerable lab for learning common web issues in a safe, offline environment.</p>
    <div class="panel-actions">
      <a class="button" href="setup.php">Initialize Database</a>
      <a class="button ghost" href="security.php">Security Level</a>
    </div>
  </div>
  <div class="panel">
    <h3>Labs</h3>
    <ul class="feature-list">
      <li>Reflected XSS</li>
      <li>Stored XSS</li>
      <li>SQL Injection</li>
    </ul>
  </div>
  <div class="panel accent">
    <h3>Safety Notes</h3>
    <p>Use only on localhost. Do not expose to the public Internet. This lab intentionally contains insecure code.</p>
  </div>
</section>

<section class="grid">
  <a class="tile" href="xss_reflected.php">
    <div class="tile-title">XSS Reflected</div>
    <div class="tile-desc">Input echoed back to the page under different security levels.</div>
  </a>
  <a class="tile" href="xss_stored.php">
    <div class="tile-title">XSS Stored</div>
    <div class="tile-desc">Messages stored in the database and rendered later.</div>
  </a>
  <a class="tile" href="sqli.php">
    <div class="tile-title">SQL Injection</div>
    <div class="tile-desc">Query user data with varying protection strategies.</div>
  </a>
  <a class="tile" href="ssrf.php">
    <div class="tile-title">SSRF</div>
    <div class="tile-desc">Server-side request behavior across security levels.</div>
  </a>
  <a class="tile" href="csrf.php">
    <div class="tile-title">CSRF</div>
    <div class="tile-desc">State-changing requests with token defenses.</div>
  </a>
</section>
<?php render_footer(); ?>
