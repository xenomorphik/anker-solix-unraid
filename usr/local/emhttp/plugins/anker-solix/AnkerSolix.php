<?php
$action = $_GET['action'] ?? $_POST['action'] ?? '';
$status_file = "/tmp/anker-solix/status.json";

if ($action === 'get_status') {
    header('Content-Type: application/json');
    if (file_exists($status_file)) {
        echo file_get_contents($status_file);
    } else {
        echo json_encode([
            "status" => "OFFLINE",
            "device_name" => "Anker SOLIX S2000",
            "battery_soc" => 0,
            "input_power_w" => 0,
            "output_power_w" => 0,
            "grid_connected" => false
        ]);
    }
    exit;
}

if ($action === 'cancel_shutdown') {
    header('Content-Type: application/json');
    file_put_contents("/tmp/anker-solix/cancel_shutdown", time());
    echo json_encode(["status" => "CANCELLED", "message" => "Pending shutdown cancelled by user."]);
    exit;
}

if ($action === 'test_auth') {
    header('Content-Type: application/json');
    $user = $_POST['user'] ?? $_GET['user'] ?? '';
    $pass = $_POST['password'] ?? $_GET['password'] ?? '';
    $country = $_POST['country'] ?? $_GET['country'] ?? 'us';

    if (empty($user) || empty($pass)) {
        echo json_encode(["success" => false, "message" => "Please enter both Username and Password before testing."]);
        exit;
    }

    $script_path = "/usr/local/emhttp/plugins/anker-solix/test_auth.py";
    $cmd = sprintf(
        "docker run --rm -v %s:/app/test_auth.py:ro anker-solix-poller:latest python3 /app/test_auth.py --user %s --password %s --country %s 2>&1",
        escapeshellarg($script_path),
        escapeshellarg($user),
        escapeshellarg($pass),
        escapeshellarg($country)
    );

    $output = shell_exec($cmd);
    $result = null;
    if ($output) {
        $lines = array_filter(array_map('trim', explode("\n", (string)$output)));
        foreach (array_reverse($lines) as $line) {
            $decoded = json_decode($line, true);
            if (is_array($decoded) && isset($decoded['success'])) {
                $result = $decoded;
                break;
            }
        }
    }

    if (is_array($result)) {
        echo json_encode($result);
    } else {
        echo json_encode([
            "success" => false,
            "message" => "Auth test failed: " . ($output ?: "Unknown error")
        ]);
    }
    exit;
}
?>
