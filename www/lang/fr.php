<?php
if (!defined('PCHTRAKT'))
	exit;



if (empty($lang) || !is_array($lang))
{
	$lang = array();
}

$lang = array_merge($lang, array(

'Empty_Login'					=>	'Le nom d\'utilisateur ne peut être vide.',
'Empty_Password'				=>	'Le mot de passe ne peut être vide.',
'Empty_LogFile'					=>	'Le nom du fichier log ne peut être vide.',
'Empty_TraktAPI'				=>	'Vous devez entrer une clé API.',
'Empty_IP'						=>	'L\'ip ne peut être vide',
'Empty_SleepTime'				=>	'Le temps d\'attente ne peut être vide.',
'Empty_RefreshTime'				=>	'Le temps de rafraichissement ne peut être vide',

'NotNumeric_SleepTime'			=>	'Le temps d\'attente doit être un entier (en minutes).',
'NotNumeric_RefreshTime'		=>	'Le temps de rafraichissement doit être un entier (en secondes).',

'Save'							=>	'Configuration mise à jour...',
'Error'							=>	'Une erreur grave est survenue..',
'Yes'							=> 	'Oui',
'No'							=> 	'Non',
'Field_Config'					=>	'Configuration de PCHTrakt',
'Field_Trakt'					=>	'Configuration de Trakt.tv',

'Login'							=>	'Utilisateur',
'Pwd'							=>	'Mot de passe',
'API_Key'						=>	'Clé API',
'IP'							=>	'IP',
'SleepTime'						=>	'Temps d\'attente',
'RefreshTime'					=>	'Temps de rafraichissement',
'LogFile'						=>	'Fichier log',
'TV_Scrobble'					=>	'Scrobbler les séries',
'Film_Scrobble'					=>	'Scrobbler les films',

'Submit'						=>	'Mettre à jour la configuration',
'Page_Title'					=>	'PchTrakt Configurator',
));
?>