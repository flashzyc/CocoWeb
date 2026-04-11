<?php
declare(strict_types=1);

header('Content-Type: text/plain; charset=utf-8');

echo "Internal service response\n";
echo "Time: " . date('Y-m-d H:i:s') . "\n";
echo "Server: " . ($_SERVER['SERVER_NAME'] ?? 'unknown') . "\n";
echo "Remote: " . ($_SERVER['REMOTE_ADDR'] ?? 'unknown') . "\n";
