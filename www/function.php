<?php
if (!defined('PCHTRAKT'))
	exit;

	function _empty() 
	{ 
		foreach(func_get_args() as $args) 
		{ 
			if( !is_numeric($args) ) 
			{ 
				if( is_array($args) ) 
				{ // Is array? 
					if( count($args, 1) < 1 ) return true; 
				} 
				elseif(!isset($args) || strlen(trim($args)) == 0) 
				{
					return true; 
				} 
			} 
		} 
		return false; 
	} 	
	
	function _checkfile($file,$content)
	{
		if (!file_exists($file))
			file_put_contents($file, $content);
	}
	
	function _checkAuth()
	{
		return ((exec('cd /share/Apps/pchtrakt && python pchtrakt.py -t')=="True")?true:false);
	}
?>