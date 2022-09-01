<?php
    // Initialize
    require '/home/maulana/vendor/autoload.php';
    use Kreait\Firebase\Factory;

    // Connect to Firebase
    $factory = (new Factory)
        ->withServiceAccount('rpi-pico-firebase-adminsdk.json')
        ->withDatabaseUri('https://rpi-pico-default-rtdb.asia-southeast1.firebasedatabase.app');
    
    $auth = $factory->createAuth();
    $database = $factory->createDatabase();

    // Get Data
    $ph = $_GET['ph'];
    $volt = $_GET['volt'];
    $previous = $_GET['previous'];
    $hash = $_GET['hash'];

    // Generate Datetime, ID, and Hash
    $datetime = date('H:i:s d-m-Y',strtotime("+7 hours"));
    $id = uniqid();

    // Send Query to Firebase
    $database->getReference('/Device/'.$id)
    ->set([
            '01-Previous' => $previous,
            '02-PH' => $ph,
            '03-Volt' => $volt,
            '04-Datetime' => $datetime,
            '05-Hash' => $hash
        ]);
?>