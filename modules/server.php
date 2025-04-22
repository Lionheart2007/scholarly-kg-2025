<?php
header("Access-Control-Allow-Origin: *");
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
    header("Access-Control-Allow-Headers: Content-Type, Authorization");
    exit(0);
}

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = ltrim($uri, '/');
$fullPath = __DIR__ . DIRECTORY_SEPARATOR . $path;

// If root path, return .ts files
if ($uri === '/' || $uri === '') {
    $jsonFiles = glob(__DIR__ . '/*.json');
    $allData = [];

    foreach ($jsonFiles as $file) {
        $content = file_get_contents($file);
        $json = json_decode($content, true);
        if ($json !== null) {
            $allData[] = $json;
        }
    }

    header('Content-Type: application/json');
    echo json_encode($allData);
    exit;
}

// If file exists, serve it
if (is_file($fullPath)) {
    $mime = mime_content_type($fullPath);
    header("Content-Type: $mime");
    readfile($fullPath);
    exit;
}

// If not found
http_response_code(404);
echo "File not found.";