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

    if (!$python) {
        $which_python = trim((string)@shell_exec("command -v python3 || command -v python"));
        $python = !empty($which_python) ? $which_python : "/usr/bin/python3";
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
    $result = json_decode($output, true);

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
