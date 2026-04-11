<?php
declare(strict_types=1);

require_once __DIR__ . '/includes/bootstrap.php';

/** @var list<string> */
const LEVEL_SAVE_ALLOWED_RETURN = [
    'index.php',
    'xss_reflected.php',
    'xss_stored.php',
    'sqli.php',
    'ssrf.php',
    'csrf.php',
    'csrf_action.php',
    'ssrf_target.php',
    'security.php',
    'setup.php',
];

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: index.php', true, 302);
    exit;
}

$level = (string) ($_POST['level'] ?? '');
set_security_level($level);

$target = (string) ($_POST['return'] ?? 'index.php');
$target = basename($target);
if (!in_array($target, LEVEL_SAVE_ALLOWED_RETURN, true)) {
    $target = 'index.php';
}

header('Location: ' . $target, true, 302);
exit;
