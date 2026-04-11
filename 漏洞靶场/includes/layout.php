<?php
declare(strict_types=1);

function current_page(): string
{
    return basename($_SERVER['SCRIPT_NAME'] ?? '');
}

function nav_link(string $href, string $label, string $current): string
{
    $active = $current === $href ? 'nav-link active' : 'nav-link';
    return '<a class="' . $active . '" href="' . $href . '">' . safe_text($label) . '</a>';
}

function render_header(string $title): void
{
    $safe_title = safe_text($title);
    $current = current_page();
    $level = security_level();
    $level_label = security_level_label($level);

    echo '<!doctype html>';
    echo '<html lang="en">';
    echo '<head>';
    echo '<meta charset="utf-8">';
    echo '<meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<title>' . $safe_title . '</title>';
    echo '<link rel="stylesheet" href="assets/app.css">';
    echo '</head>';
    echo '<body>';
    echo '<div class="bg-shape shape-1"></div>';
    echo '<div class="bg-shape shape-2"></div>';
    echo '<header class="site-header">';
    echo '<div class="brand">';
    echo '<div class="brand-mark">C0C0</div>';
    echo '<div class="brand-text">';
    echo '<div class="brand-title">CocoWeb</div>';
    echo '<div class="brand-subtitle">Local Security Lab</div>';
    echo '</div>';
    echo '</div>';
    echo '<nav class="nav">';
    echo nav_link('index.php', 'Dashboard', $current);
    echo nav_link('xss_reflected.php', 'XSS Reflected', $current);
    echo nav_link('xss_stored.php', 'XSS Stored', $current);
    echo nav_link('sqli.php', 'SQL Injection', $current);
    echo nav_link('ssrf.php', 'SSRF', $current);
    echo nav_link('csrf.php', 'CSRF', $current);
    echo nav_link('security.php', 'Security Level', $current);
    echo nav_link('setup.php', 'Setup', $current);
    echo '</nav>';
    echo '<div class="level-indicator">';
    echo '<form class="header-level-form" method="post" action="level_save.php">';
    echo '<input type="hidden" name="return" value="' . safe_text($current) . '">';
    echo '<label class="visually-hidden" for="header-security-level">Security level</label>';
    echo '<select class="header-level-select" id="header-security-level" name="level" aria-label="Security level" onchange="this.form.submit()">';
    foreach (SECURITY_LEVELS as $opt) {
        $selected = $opt === $level ? ' selected' : '';
        echo '<option value="' . safe_text($opt) . '"' . $selected . '>' . safe_text(security_level_label($opt)) . '</option>';
    }
    echo '</select>';
    echo '</form>';
    echo '</div>';
    echo '</header>';
    echo '<main class="container">';
    echo '<div class="page-title">';
    echo '<h1>' . $safe_title . '</h1>';
    echo '<div class="page-meta">Security level: <strong>' . $level_label . '</strong></div>';
    echo '</div>';
}

function render_footer(): void
{
    echo '<footer class="site-footer">';
    echo '<div>Use only on a local machine. Do not expose to the Internet.</div>';
    echo '</footer>';
    echo '</main>';
    echo '</body>';
    echo '</html>';
}

function render_notice(string $text, string $type = 'info'): void
{
    $class = 'notice';
    if ($type === 'success') {
        $class .= ' notice-success';
    } elseif ($type === 'error') {
        $class .= ' notice-error';
    } elseif ($type === 'warn') {
        $class .= ' notice-warn';
    }
    echo '<div class="' . $class . '">' . safe_text($text) . '</div>';
}
