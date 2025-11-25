<?php
header('Content-Type: application/json');

// Stub login logic
$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';

if ($username === 'admin' && $password === 'admin') {
    echo json_encode([
        'success' => true,
        'session' => [
            'username' => 'Admin',
            'is_admin' => true
        ]
    ]);
} else {
    echo json_encode([
        'success' => false,
        'message' => 'Invalid credentials'
    ]);
}
?>
