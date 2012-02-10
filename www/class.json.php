<?php
if (!defined('PCHTRAKT'))
	exit;

class JSON { 

    private static $instance; 
    private $content; 
	private $ini_file;
	
	private function __construct($ini_file) { 
		$this->ini_file  = $ini_file;
        $this->content = file_get_contents($ini_file); 		
    } 
    
    public static function getInstance($ini_file) { 
        if(! isset(self::$instance)) { 
            self::$instance = new JSON($ini_file);            
        } 
        return self::$instance; 
    } 
    
    public function __get($key) {
		preg_match('('. $key .' = "(.*)",)', $this->content, $matches);
		return $matches[1];
    } 

} 	
?>	
	