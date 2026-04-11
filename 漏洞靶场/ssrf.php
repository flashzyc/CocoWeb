<?php
require_once __DIR__ . '/includes/bootstrap.php';

function fetch_url(string $url): array
{
    $status = '';
    $body = '';
    $error = null;

    $context = stream_context_create([
        'http' => [
            'timeout' => 4,
            'ignore_errors' => true,
            'user_agent' => 'CocoWeb-SSRF'
        ]
    ]);

    $result = @file_get_contents($url, false, $context);
    if ($result !== false) {
        $body = $result;
        if (isset($http_response_header[0])) {
            $status = $http_response_header[0];
        }
        return [$status, $body, null];
    }

    if (function_exists('curl_init')) {
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 4);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
        curl_setopt($ch, CURLOPT_USERAGENT, 'CocoWeb-SSRF');
        $body = curl_exec($ch);
        if ($body === false) {
            $error = curl_error($ch);
        } else {
            $status = 'HTTP ' . curl_getinfo($ch, CURLINFO_HTTP_CODE);
        }
        curl_close($ch);
        return [$status, $body ?: '', $error];
    }

    return ['', '', 'No available HTTP client in PHP configuration.'];
}

function is_allowed_medium(string $url): bool
{
    $parts = parse_url($url);
    if (!$parts || empty($parts['scheme'])) {
        return false;
    }
    $scheme = strtolower($parts['scheme']);
    if (!in_array($scheme, ['http', 'https'], true)) {
        return false;
    }
    return true;
}

function is_allowed_high(string $url): bool
{
    $parts = parse_url($url);
    if (!$parts || empty($parts['scheme']) || empty($parts['host'])) {
        return false;
    }
    $scheme = strtolower($parts['scheme']);
    if (!in_array($scheme, ['http', 'https'], true)) {
        return false;
    }
    $host = strtolower($parts['host']);
    $allowed = ['127.0.0.1', 'localhost'];
    if (!in_array($host, $allowed, true)) {
        return false;
    }
    return true;
}

$url = $_POST['url'] ?? '';
$result = null;
$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $level = security_level();
    $allowed = true;
    if ($level === 'medium') {
        $allowed = is_allowed_medium($url);
    } elseif ($level === 'high') {
        $allowed = is_allowed_high($url);
    }

    if (!$allowed) {
        $error = 'Request blocked by security policy.';
    } else {
        [$status, $body, $fetch_error] = fetch_url($url);
        if ($fetch_error) {
            $error = $fetch_error;
        } else {
            $result = [
                'status' => $status ?: 'OK',
                'body' => $body
            ];
        }
    }
}

render_header('SSRF');
?>

<div class="panel">
  <form class="form" method="post" action="ssrf.php">
    <div class="form-row">
      <label for="url">URL to fetch</label>
      <input id="url" name="url" type="text" value="<?php echo safe_text($url); ?>" placeholder="http://127.0.0.1/cocoweb/ssrf_target.php">
    </div>
    <button class="button" type="submit">Fetch</button>
  </form>
  <p class="muted hint">Try: <code>http://127.0.0.1/cocoweb/ssrf_target.php</code></p>
</div>

<?php if ($error): ?>
  <?php render_notice($error, 'error'); ?>
<?php endif; ?>

<?php if ($result): ?>
  <div class="panel">
    <h3>Response</h3>
    <p class="muted"><?php echo safe_text($result['status']); ?></p>
    <pre class="code"><?php echo safe_text(substr($result['body'], 0, 2000)); ?></pre>
  </div>
<?php endif; ?>

<div class="panel">
  <h3>Notes</h3>
  <ul class="feature-list">
    <li>Low: no validation.</li>
    <li>Medium: only allows http/https.</li>
    <li>High: allowlist for localhost only.</li>
  </ul>
</div>

<?php render_footer(); ?>
