<?php
if (!defined('PCHTRAKT'))
	exit;



if (empty($lang) || !is_array($lang))
{
	$lang = array();
}

$lang = array_merge($lang, array(


/* PCHTrakt Key */
'PCHTrakt_Config'					=>	'PCHTrakt Configuration',
'PCHTrakt_Empty_LogFile'			=>	'LogFile must be set.',
'PCHTrakt_Empty_API'				=>	'Trakt API Key must be set.',
'PCHTrakt_Empty_IP'					=>	'IP must be set.',
'PCHTrakt_Empty_SleepTime'			=>	'Sleep time must be set.',
'PCHTrakt_NotNumeric_SleepTime'		=>	'Sleep time must be a numeric >= '. SEC_LOW .'.',

'PCHTrakt_API'						=>	'API Key',
'PCHTrakt_IP'						=>	'IP',
'PCHTrakt_SleepTime'				=>	'Sleep time',
'PCHTrakt_LogFile'					=>	'Log file',

/* Trakt Key */
'Trakt_Config'						=>	'Trakt.tv Configuration',
'Trakt_Empty_Login'					=>	'Trakt login must be set.',
'Trakt_Empty_Password'				=>	'Trakt password must be set.',
'Trakt_Empty_RefreshTime'			=>	'Refresh Time must be set.',
'Trakt_NotNumeric_RefreshTime'		=>	'Refresh Time must be a numeric >= ' . MIN_LOW .'.',
'Trakt_Failed'  					=>  'Connexion to Trakt.tv site is impossible. Check your login and password.',
'Trakt_RefreshTime'					=>	'Refresh time',

/* BetaSeries Key */
'BetaSeries_Config'					=>	'BetaSeries.com Configuration',
'BetaSeries_Empty_Login'			=>	'BetaSeries login must be set.',
'BetaSeries_Empty_Password'			=>	'BetaSeries password must be set.',
'BetaSeries_Failed'  				=>  'Connexion to BetaSeries.com site is impossible. Check your login and password.',


/*General Key */
'Page_Title'						=>	'PchTrakt Configurator',

'Save'								=>	'Configuration is updated...',
'Error'								=>	'OOps something is broken...',

'Yes'								=> 	'Yes',
'No'								=> 	'No',

'Login'								=>	'Login',
'Pwd'								=>	'Password',




'TV_Scrobble'						=>	'TV-Show scrobble',
'Film_Scrobble'						=>	'Film scrobble',

'Submit'							=>	'Update my configuration',

'sec'								=>	'seconds',
'min'								=>	'minutes',



));
?>