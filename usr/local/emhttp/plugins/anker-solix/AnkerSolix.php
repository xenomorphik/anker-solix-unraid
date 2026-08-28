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
?>
