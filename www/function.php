<?php
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
?>