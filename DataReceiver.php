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

    // Get Data and Hash
    $id = $_GET['id'];
    $previous = $_GET['previous'];
    $ph = $_GET['ph'];
    $hash = $_GET['hash'];

    $id = sprintf("%03d", $id);

    print($id." ".$ph." ".$hash);

    // Send Query to Firebase
    //$database->getReference('/Device1/00-Block_'.$id)
    //->set([
    //        '01-Previous' => $previous,
    //        '02-Data' => $ph,
    //        '03-Hash' => $hash
    //    ]);
?>