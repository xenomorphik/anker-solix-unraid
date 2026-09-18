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
            "power_source" => "Unknown",
            "battery_percentage" => 0,
            "evaluation" => ["state" => "OFFLINE", "reason" => "Status file missing"]
        ]);
    }
    exit;
}

if ($action === 'cancel_shutdown') {
    header('Content-Type: application/json');
    // Signal file to cancel pending countdown
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

    $plugin_dir = "/usr/local/emhttp/plugins/anker-solix";
    $python_candidates = [
        "$plugin_dir/venv/bin/python3",
        "/usr/bin/python3",
        "/usr/local/bin/python3",
        "/usr/bin/python",
        "/bin/python3"
    ];

    $python = null;
    foreach ($python_candidates as $candidate) {
        if (@file_exists($candidate) && @is_executable($candidate)) {
            $python = $candidate;
            break;
        }
    }

    if (!$python || !@file_exists($python)) {
        $which_python = trim((string)@shell_exec("command -v python3 || command -v python"));
        if (!empty($which_python) && @file_exists($which_python)) {
            $python = $which_python;
        } else {
            echo json_encode([
                "success" => false,
                "message" => "Python 3 is missing on your Unraid server. Please re-install the anker-solix plugin to auto-install Python 3."
            ]);
            exit;
        }
    }

    $client_script = "$plugin_dir/solix_client.py";

    $cmd = sprintf(
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin %s %s --test-auth --user %s --password %s --country %s 2>&1",
        escapeshellcmd($python),
        escapeshellarg($client_script),
        escapeshellarg($user),
        escapeshellarg($pass),
        escapeshellarg($country)
    );

    $output = shell_exec($cmd);
    
    // Find valid JSON payload in output lines
    $result = null;
    if ($output) {
        $lines = array_filter(array_map('trim', explode("\n", (string)$output)));
        foreach (array_reverse($lines) as $line) {
            $decoded = json_decode($line, true);
            if (is_array($decoded)) {
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
            "message" => "Auth test output error: " . ($output ?: "Unknown error")
        ]);
    }
    exit;
}
?>
