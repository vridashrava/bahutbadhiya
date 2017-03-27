<?php
$servername = "localhost";
$username = "vichaark_signup";
$password = "modi is great";
$dbname = "vichaark_bblabs";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    //die("Connection failed: " . $conn->connect_error);
    error_log("Connection failed: ". $conn->connect_error);
    $ERROR = TRUE;
    $ERROR_MESSAGE = "Could not register into database";
} 

if (!$ERROR) {
    /* Check if email already exists */
    $sql = "SELECT * from registered_users where emailid = '$email'";
    $result = mysqli_query($conn, $sql);
    //error_log("RESULT ROWS: ".$result->num_rows, 0);

    if ($result && ($result->num_rows > 0)) {
    	// exists
	error_log("Email: " .$email ." already in the database", 0);
	$ERROR = TRUE;
	$ERROR_MESSAGE = "Email already registered with us";
    } else {
	$ERROR = FALSE;
    }
}

if (!$ERROR) {
	/* Insert now that it is not in our database */
	$sql = "INSERT INTO registered_users (emailid)
	VALUES ('$email')";

	if ($conn->query($sql) === TRUE) {
	    //echo "New record created successfully";
	} else {
	    //echo "Error: " . $sql . "<br>" . $conn->error;
	    error_log("Error: " .$sql . $conn->error, 0);
	    $ERROR = TRUE;
	    $ERROR_MESSAGE = "Could not register into database";
	}


	$conn->close();
}
?>
