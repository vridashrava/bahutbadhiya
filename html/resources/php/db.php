<?
class DB {
    #private $servername = "localhost";
    #private $username = "vichaark_signup";
    #private $password = "modi is great";
    #private $dbname = "vichaark_bblabs";

    private $servername = "localhost";
    private $username = "bbweb";
    private $password = "modi is great";
    private $dbname = "bahutbadhiya";

    private $conn = NULL;
    private $ERROR = FALSE;
    private $ERROR_MESSAGE = "";

    public function __construct() {
        //parent::__construct();
        
        // Create connection
        $this->conn = new mysqli($this->servername, $this->username, $this->password, $this->dbname);

        // Check connection
        if ($this->conn->connect_error) {
            //die("Connection failed: " . $conn->connect_error);
            error_log("Connection failed: ". $this->conn->connect_error);
            $this->ERROR = TRUE;
            $this->ERROR_MESSAGE = "Could not register into database";
        }

    }


    public function results($query) {
        If (!$this->ERROR) {
	    //first set UTF-8
	    $result = mysqli_query($this->conn, "SET NAMES utf8");
            $result = mysqli_query($this->conn, $query);
            return $result;
        }
        
        return NULL;
    }
    
    public function results_as_array($query) {
        $results  = $this->results($query);
        $myArray = array();

        if ($results) {
            while($row = $results->fetch_array(MYSQL_ASSOC)) {
                    $myArray[] = $row;
            }

            //error_log("Array: " . $myArray);
            return $this->utf8ize($myArray);
            $results->close();
        }
        else {
            return NULL;
            error_log("Error fetching results for query: ". $query);
        }
    }
    
    public function results_as_json($query) {
        $results_array = results_as_array($query);
        if ($results_array) {
            return json_encode($this->utf8ize($results_array), JSON_PRETTY_PRINT);
        }
        else {
            return '{"ERROR": "Error fetching results"}';
        }
    }
    
    private function utf8ize($d) {
        if (is_array($d)) {
            foreach ($d as $k => $v) {
                $d[$k] = $this->utf8ize($v);
            }
        } 
        else if (is_string ($d)) {
            return utf8_encode($d);
        }
        return $d;
    }

}

?>
