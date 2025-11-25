<?php
header('Content-Type: application/json');

// Event schedule with time, days, and category
$events = [
    [
        'name' => 'Blood Castle',
        'time' => '00:00',
        'days' => ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'category' => 'Mini-Game'
    ],
    [
        'name' => 'Devil Square',
        'time' => '01:00',
        'days' => ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'category' => 'Mini-Game'
    ],
    [
        'name' => 'Chaos Castle',
        'time' => '02:00',
        'days' => ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'category' => 'PvP'
    ],
    [
        'name' => 'Golden Invasion',
        'time' => '12:00',
        'days' => ['Sat', 'Sun'],
        'category' => 'Boss'
    ],
    [
        'name' => 'Red Dragon',
        'time' => '20:00',
        'days' => ['Fri', 'Sat', 'Sun'],
        'category' => 'Boss'
    ],
    [
        'name' => 'Castle Siege',
        'time' => '19:00',
        'days' => ['Sat'],
        'category' => 'Guild'
    ]
];

echo json_encode(['events' => $events]);
?>
