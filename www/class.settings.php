<?php
if (!defined('PCHTRAKT'))
	exit;

class Settings { 

    private static $instance; 
    private $settings;
    private $ini_file;
	
	
	
	private function __construct($ini_file) { 
		$this->ini_file  = $ini_file;
		/* setting is a array with true  */
        $this->settings = parse_ini_file($ini_file, true); 
    } 
    
    public static function getInstance($ini_file) { 
        if(! isset(self::$instance)) { 
            self::$instance = new Settings($ini_file);            
        } 
        return self::$instance; 
    } 
	
    function getSection($key) { 
        return $this->settings[$key]; 
    } 
     
	 
	function get($section,$key=NULL) { 
        if(is_null($key)) return $this->getSection($section); 
        return $this->getValue($section, $key); 
    } 
     
    function setSection($section,$array) { 
        if(!is_array($array)) return false; 
        return $this->settings[$section] = $array; 
    } 
     
	function setValue($section,$key,$value) { 
        if($this->settings[$section][$key] = $value ) return true; 
    } 
     
    function set($section,$key,$value=NULL) { 
        if(is_array($key) && is_null($value)) return $this->setSection($section, $key); 
        return $this->setValue($section, $key, $value); 
    } 	 
	
	function getValue( $section, $key ) { 
        if(!isset($this->settings[$section])) return false; 
        return $this->settings[$section][$key]; 
    } 		
	
	private function reload() { 
		self::$instance = new Settings($this->ini_file);
    }	
		
	/* save file after modification */
	public function save() { 
		try {		
			$content = '';
			foreach($this->settings as $section => $array){ 
				$content .= "[" . $section . "]\n"; 
				foreach($array as $key => $value) { 
					$content .= "$key = $value\n"; 
				} 
				$content .= "\n";
			} 
			file_put_contents($this->ini_file,$content);
			unset($content);
			$this->reload();			
			return true; 
		} 
		catch (Exception $e) {
			return false;
		}
    }
		
	/* easy debug */
	public function debug()
	{
		print '<div class="info" id="info">';
		foreach($this->settings as $section => $array){ 
			print  "<strong><u>[" . $section . "]</u></strong><br />"; 
			foreach($array as $key => $value) { 
				print "<strong>[$key]</strong> = <i>$value</i><br />";
			} 
			print "<br />";
		} 
		print '</div>';
	}
} 	
?>	