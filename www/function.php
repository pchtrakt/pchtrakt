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
	
	function _execPy()
	{
		exec('cd /share/Apps/pchtrakt && ./daemon.sh restart');
	}	
	
	function _bool($in, $strict=false) 
	{
		$out = null;
		// if not strict, we only have to check if something is false
		if (in_array($in,array('false', 'False', 'FALSE', 'no', 'No', 'n', 'N', '0', 'off','Off', 'OFF', false, 0, null), true)) 
		{
			$out = false;
		} 
		else if ($strict) 
		{
			// if strict, check the equivalent true values
			if (in_array($in,array('true', 'True', 'TRUE', 'yes', 'Yes', 'y', 'Y', '1','on', 'On', 'ON', true, 1), true)) 
				$out = true;

		} 
		else 
		{
			// not strict? let the regular php bool check figure it out (will largely default to true)
			$out = ($in?true:false);
		}
		return $out;
	}
?>