<?php
if (!defined('PCHTRAKT'))
	exit;

class Settings { 

    private static $instance; 
    private $settings; 
    private $ini_file;
	
	private function __construct($ini_file) { 
		$this->ini_file  = $ini_file;
        $this->settings = parse_ini_file($ini_file, false); 
    } 
    
    public static function getInstance($ini_file) { 
        if(! isset(self::$instance)) { 
            self::$instance = new Settings($ini_file);            
        } 
        return self::$instance; 
    } 
    
    public function __get($key) {
		return $this->settings[$key];
    } 
    public function __set($key,$value) {
        $this->settings[$key] = $value;
    }
	
	/* get section name */	
	private function getMasterSection() {
        $match = '';
        $file = fopen($this->ini_file, "r" );
        $fdata = fread($file,filesize($this->ini_file));
        preg_match('/\[(.*)\]/', $fdata, $match);
        fclose($file);
        return "[".$match[1]."]\n";
    }
	private function reload() { 
        $this->settings = parse_ini_file($this->ini_file, false); 
    }	

	/* save file after modification */
	public function save() { 
		try {
			$content = $this->getMasterSection();
			foreach( $this->settings as $key => $value ) {
				$content .= "$key=$value\n";
			}
			$content .= "\n";
			file_put_contents($this->ini_file,$content);
			file_put_contents(rtrim(dirname($this->ini_file), "/\\")."/".$this->log_file,date("m.d.y H:i:s") ." => save the data\n", FILE_APPEND | LOCK_EX);
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
		foreach( $this->settings as $key => $value ) {
			print "<strong>[$key]</strong> = <i>$value</i><br />";
		}
		print '</div>';
	}
} 	
?>	
	