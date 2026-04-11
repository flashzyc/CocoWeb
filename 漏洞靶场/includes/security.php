<?php
declare(strict_types=1);

const SECURITY_LEVELS = ['low', 'medium', 'high'];

function security_level(): string
{
    $level = $_SESSION['security_level'] ?? 'low';
    if (!in_array($level, SECURITY_LEVELS, true)) {
        $level = 'low';
        $_SESSION['security_level'] = $level;
    }
    return $level;
}

function set_security_level(string $level): void
{
    if (in_array($level, SECURITY_LEVELS, true)) {
        $_SESSION['security_level'] = $level;
    }
}

function security_level_label(string $level): string
{
    switch ($level) {
        case 'medium':
            return 'Medium';
        case 'high':
            return 'High';
        default:
            return 'Low';
    }
}

function security_badge_class(string $level): string
{
    switch ($level) {
        case 'medium':
            return 'badge badge-medium';
        case 'high':
            return 'badge badge-high';
        default:
            return 'badge badge-low';
    }
}

function safe_text(string $value): string
{
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function xss_medium_filter(string $value): string
{
    $value = preg_replace('/<\\s*\\/?\\s*script\\b/i', '', $value);
    $value = preg_replace('/on\\w+\\s*=\\s*/i', '', $value);
    return $value ?? '';
}

function xss_reflected_output(string $value): string
{
    $level = security_level();
    if ($level === 'low') {
        return $value;
    }
    if ($level === 'medium') {
        return xss_medium_filter($value);
    }
    return safe_text($value);
}

function xss_store_input(string $value): string
{
    $level = security_level();
    if ($level === 'low') {
        return $value;
    }
    if ($level === 'medium') {
        return xss_medium_filter($value);
    }
    return $value;
}

function xss_store_output(string $value): string
{
    $level = security_level();
    if ($level === 'high') {
        return safe_text($value);
    }
    return $value;
}
