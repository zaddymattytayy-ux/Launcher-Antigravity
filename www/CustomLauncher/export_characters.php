<?php
header('Content-Type: application/json');

// Stub emulator detection
$emulator = 'louis'; // Default to Louis

// Stub character data
$characters = [
    ['name' => 'Player1', 'class' => 'Dark Knight', 'level' => 400, 'resets' => 50],
    ['name' => 'Player2', 'class' => 'Soul Master', 'level' => 350, 'resets' => 40]
];

echo json_encode([
    'emulator' => $emulator,
    'characters' => $characters
]);
?>
