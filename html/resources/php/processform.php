<?
$ERROR = FALSE;
$ERROR_MESSAGE = "";
$NOT_SUBMITTED_YET = TRUE;


function isvalid($email) {
    return TRUE;
}

/* Get the email address */
if(isset($_POST['email'])) {
  $NOT_SUBMITTED_YET = FALSE;
  if (isvalid($_POST['email'])) {
     $email = $_POST['email'];
  }
  else {
    $ERROR = TRUE;
    $ERROR_MESSAGE = "Invalid Email";
  }
}

if (!$NOT_SUBMITTED_YET && !$ERROR) {
  /* Insert into DB */
  include('dbinsert.php');
}

if ($NOT_SUBMITTED_YET || $ERROR) {
  /* Show the input form */
  echo "<style>        

        .form-submitted {
            display: none;
        }
    </style>";

}
else {
 /* Show the submit status */
   echo "<style>        
        .form-input {
            display: none;
        }

    </style>";
}

?>

