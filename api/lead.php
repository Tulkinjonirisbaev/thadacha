<?php
// Приём заявки с лендинга и отправка в Telegram.
// Токен бота хранится только на сервере: в api/config.php или в переменных окружения.
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');

function done(int $code, array $body): void {
    http_response_code($code);
    echo json_encode($body, JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') done(405, ['ok' => false, 'error' => 'method']);

$cfg = is_file(__DIR__ . '/config.php') ? require __DIR__ . '/config.php' : [];
$token = $cfg['bot_token'] ?? getenv('TG_BOT_TOKEN') ?: '';
$chat  = $cfg['chat_id']   ?? getenv('TG_CHAT_ID')   ?: '';
if ($token === '' || $chat === '') done(500, ['ok' => false, 'error' => 'not_configured']);

$raw = file_get_contents('php://input', false, null, 0, 8192);
$in  = json_decode($raw ?: '', true);
if (!is_array($in)) $in = $_POST;

// Ловушка для ботов: скрытое поле у человека остаётся пустым.
if (!empty($in['website'])) done(200, ['ok' => true]);

$f = [];
foreach (['name', 'company', 'phone', 'seats', 'hosting'] as $k) {
    $v = trim((string)($in[$k] ?? ''));
    $f[$k] = mb_substr(preg_replace('/\s+/u', ' ', $v), 0, 120);
}
if ($f['name'] === '' || $f['company'] === '' || !preg_match('/^[\d\s()+\-]{7,20}$/', $f['phone'])) {
    done(422, ['ok' => false, 'error' => 'validation']);
}

$e = fn(string $s): string => htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
$text = "<b>Новая заявка с лендинга Thadacha</b>\n\n"
      . "Имя: {$e($f['name'])}\n"
      . "Компания: {$e($f['company'])}\n"
      . "Телефон: {$e($f['phone'])}\n"
      . "Сотрудников: {$e($f['seats'])}\n"
      . "Размещение: {$e($f['hosting'])}\n"
      . 'Время: ' . (new DateTime('now', new DateTimeZone('Asia/Tashkent')))->format('d.m.Y H:i');

$ch = curl_init("https://api.telegram.org/bot{$token}/sendMessage");
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 10,
    CURLOPT_POSTFIELDS => ['chat_id' => $chat, 'text' => $text, 'parse_mode' => 'HTML'],
]);
$res  = curl_exec($ch);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($res === false || $code !== 200) {
    error_log('thadacha lead: telegram ' . $code . ' ' . substr((string)$res, 0, 200));
    done(502, ['ok' => false, 'error' => 'telegram']);
}
done(200, ['ok' => true]);
