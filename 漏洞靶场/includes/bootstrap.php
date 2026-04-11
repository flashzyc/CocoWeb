<?php
declare(strict_types=1);

session_start();

if (!isset($_SESSION['security_level'])) {
    $_SESSION['security_level'] = 'low';
}

$CONFIG = require __DIR__ . '/config.php';

function config(string $key)
{
    global $CONFIG;
    return $CONFIG[$key] ?? null;
}

require_once __DIR__ . '/security.php';
require_once __DIR__ . '/layout.php';
require_once __DIR__ . '/db.php';
