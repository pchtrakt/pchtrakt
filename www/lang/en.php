<?php
if (!defined('PCHTRAKT'))
	exit;



if (empty($lang) || !is_array($lang))
{
	$lang = array();
}

$lang = array_merge($lang, array(

'Empty_Login'					=>	'Login must be set.',
'Empty_Password'				=>	'Password must be set.',
'Empty_LogFile'					=>	'LogFile must be set.',
'Empty_TraktAPI'				=>	'Trakt API Key must be set.',
'Empty_IP'						=>	'IP must be set.',
'Empty_SleepTime'				=>	'Sleep time must be set.',
'Empty_RefreshTime'				=>	'Refresh Time must be set.',

'NotNumeric_SleepTime'			=>	'Sleep time must be a numeric >= '. SEC_LOW .'.',
'NotNumeric_RefreshTime'		=>	'Refresh Time must be a numeric >= ' . MIN_LOW .'.',

'Save'							=>	'Configuration is updated...',
'Error'							=>	'OOps something is broken...',
'Yes'							=> 	'Yes',
'No'							=> 	'No',
'Field_Config'					=>	'PCHTrakt Configuration',
'Field_Trakt'					=>	'Trakt.tv Configuration',

'Login'							=>	'Login',
'Pwd'							=>	'Password',
'API_Key'						=>	'API Key',
'IP'							=>	'IP',
'SleepTime'						=>	'Sleep time',
'RefreshTime'					=>	'Refresh time',
'LogFile'						=>	'Log file',
'TV_Scrobble'					=>	'TV-Show scrobble',
'Film_Scrobble'					=>	'Film scrobble',

'Submit'						=>	'Update my configuration',
'Page_Title'					=>	'PchTrakt Configurator',

'sec'							=>	'seconds',
'min'							=>	'minutes',
'TraktAccount_Failed'  			=>  'Connexion to Trakt.tv site is impossible. Check your login and password.',
));
?>