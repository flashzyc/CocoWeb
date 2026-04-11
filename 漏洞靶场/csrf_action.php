<?php
require_once __DIR__ . '/includes/bootstrap.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: csrf.php');
    exit;
}

$conn = require_db();
$level = security_level();

$user_id = (int) ($_POST['user_id'] ?? 0);
$email = trim((string) ($_POST['email'] ?? ''));
$token = (string) ($_POST['token'] ?? '');

if ($user_id <= 0 || $email === '') {
    $_SESSION['csrf_notice'] = ['message' => 'User and email are required.', 'type' => 'warn'];
    header('Location: csrf.php');
    exit;
}

if ($level === 'medium') {
    if ($token !== 'cocoweb_medium_token') {
        $_SESSION['csrf_notice'] = ['message' => 'Invalid CSRF token (medium).', 'type' => 'error'];
        header('Location: csrf.php');
        exit;
    }
} elseif ($level === 'high') {
    $session_token = (string) ($_SESSION['csrf_token'] ?? '');
    if ($session_token === '' || !hash_equals($session_token, $token)) {
        $_SESSION['csrf_notice'] = ['message' => 'Invalid CSRF token (high).', 'type' => 'error'];
        header('Location: csrf.php');
        exit;
    }
}

$stmt = $conn->prepare("UPDATE users SET email = ? WHERE id = ?");
if (!$stmt) {
    $_SESSION['csrf_notice'] = ['message' => 'Update failed: ' . $conn->error, 'type' => 'error'];
    header('Location: csrf.php');
    exit;
}

$stmt->bind_param('si', $email, $user_id);
$stmt->execute();
$stmt->close();

$_SESSION['csrf_notice'] = ['message' => 'Email updated.', 'type' => 'success'];
header('Location: csrf.php');
exit;
