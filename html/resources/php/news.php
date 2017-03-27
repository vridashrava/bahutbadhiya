<?php
    include('db.php');

    $db = new DB();
    $results_l3 = $db->results_as_array('select * from articles where feedid <> 322 and description is not null and description <> "" order by pubdate desc limit 10');

    header('Content-Type: application/json');
    header('Access-Control-Allow-Origin: http://127.0.0.1:50773');
    
    $results_l2["docs"] = $results_l3;
    $results_l1["response"] = $results_l2;

    $results = json_encode($results_l1, JSON_PRETTY_PRINT);
    echo $results;
    
?>
