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

    // Test authentication inside Docker container where Python 3.12 and anker_solix_api are installed
    $py_code = sprintf(
        "import asyncio, aiohttp, json; from anker_solix_api import api; async def t(): async with aiohttp.ClientSession() as s: a = api.AnkerSolixApi(%s, %s, %s, websession=s); res = await a.update_sites(); print(json.dumps({'success': True, 'message': 'Authentication successful. Found %%d bound devices.' %% len(a.devices)})); asyncio.run(t())",
        var_export($user, true),
        var_export($pass, true),
        var_export($country, true)
    );

    $cmd = sprintf(
        "docker run --rm anker-solix-poller:latest python3 -c %s 2>&1",
        escapeshellarg($py_code)
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
            "message" => "Auth failed: " . ($output ?: "Could not authenticate with Anker Cloud")
        ]);
    }
    exit;
}
?>
