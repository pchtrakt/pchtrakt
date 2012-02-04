<?php
// define some constant 
define('DEBUG',false);
define('INI_PATH','../../pchtrakt/');
define('INI_FILE','pchtrakt.ini');
define('PAGE_TITLE','PCHTrakt Configurator');
define('CSS_FILE','pchtrakt.css');
// PchTrakt dvp key
define('APIKEY','def6943c09e19dccb4df715bd4c9c6c74bc3b6d7');

// require some script
require_once 'function.php';
require_once 'class.settings.php';



// load settings from the ini file
$conf = Settings::getInstance(INI_PATH.''.INI_FILE); 

?>
<html>
<head>
	<title><?php echo PAGE_TITLE;?></title>
	<style type="text/css">@import url("<?php echo CSS_FILE;?>");</style>
</head>
<body>

<form id="pchtrakt_from" name="pchtrakt_from" method="post" action="">
	<?php
	


	if ($_SERVER['REQUEST_METHOD']=='POST' && ($_POST['Submit']) ) { 
		$boolTV = true;
		$boolFilm = true;
		$save = true;
		foreach ($_POST as $key => $value) { 
			if (DEBUG) echo '<br />key.'.$key;
			
			switch ($key) {
				case 'trakt_Login':
					$trakt_Login=$value;
					if (_empty($value)){$save=false;print'login must be set<br />';}
					break;
				case 'trakt_Password':
					$trakt_Password=$value;
					if (_empty($value)){$save=false;print'Password must be set<br />';}
					break;
				case 'trakt_API':
					$trakt_API=$value;
					if (DEBUG && _empty($value)){ $save=false; print'Trakt API Key must be set<br />';}
					break;
				case 'APP_IP':
					$APP_IP=$value;
					if (DEBUG && _empty($value)){ $save=false; print'IP must be set<br />';}
					break;
				case 'APP_SleepTime':
					$APP_SleepTime=$value;
					if (_empty($value)){$save=false; print'Sleep Time  must be set<br />';}
					else{
						if(!is_numeric($value)){$save=false; print'Sleep Time must be a numeric<br />';}
					}
					break;
				case 'APP_RefreshTime':
					$APP_RefreshTime=$value;
					if (_empty($value)){ $save=false; print'Refresh Time must be set<br />';}
					else{
						if(!is_numeric($value)){$save=false; print'Refresh Time must be a numeric<br />';}
					}
					break;
				case 'APP_TVScrobble':
					$APP_TVScrobble=$value;
					if ($value==0) {$boolTV=false;}
					break;
				case 'APP_FilmScrobble':
					$APP_FilmScrobble=$value;
					if ($value==0) {$boolFilm=false;}
					break;	
				case 'APP_LogFile':
					$APP_LogFile=$value;
					if (DEBUG && _empty($value)){$save=false; print'LogFile must be set<br />';}
					break;						
			}
		}	 
		
		if ( !$boolTV && !$boolFilm){ $save=false; echo '<br />Why do you use the PCHTrakt App if you don\'t want to scrobble ????';}			
		
		if ($save)
		{
			$conf->write();
		}
		else{ /* TODO display error message */
		}
	} 
	?>
	
	
  <fieldset>
  <legend>Trakt.tv Information</legend>
  <label for="trakt_Login">Login:</label> 
  <input type="text" name="trakt_Login" id="trakt_Login" value="<?php if(isset($trakt_Login)){print $trakt_Login;}else{print $conf->trakt_login;} ?>" />
  <br />  <br />
  <label for="trakt_Password">Password:</label>
  <input type="password" name="trakt_Password" id="trakt_Password" value="<?php if(isset($trakt_Password)){print $trakt_Password;}else{print $conf->trakt_pwd;} ?>" />
  <?php if (DEBUG) { ?>
	<br />  <br />
  <label for="trakt_API">API Key:</label>
  <input type="text" name="trakt_API" id="trakt_API" value="<?php echo APIKEY;?>" />

  <?php } ?>  
  </fieldset> 
  <br />  <br />
  <fieldset>
 
  <legend>PCHTrakt Configuration</legend>
  <?php if (DEBUG) { ?>
  <label for="APP_IP">IP:</label>
  <input type="text" name="APP_IP" id="APP_IP" value="<?php  if(isset($APP_IP)){ print $APP_IP; }else{echo $conf->pch_ip;}?>" />
  <br />  <br />
  <?php } ?>
  
  <label for="APP_SleepTime">Sleep time:</label>
  <input type="text" name="APP_SleepTime" id="APP_SleepTime" value="<?php  if(isset($APP_SleepTime)){ print $APP_SleepTime; }else{echo $conf->sleep_time;}?>"/>
  <br />  <br />
  
  <label for="APP_RefreshTime">Refresh time:</label>
  <input type="text" name="APP_RefreshTime" id="APP_RefreshTime" value="<?php  if(isset($APP_RefreshTime)){ print $APP_RefreshTime; }else{echo $conf->refresh_time;}?>"/>
  <br />  <br />
  
  <label for="APP_TVScrobble">TV-Show scrobble:</label>
  <select id="APP_TVScrobble" name="APP_TVScrobble">
	<option <?php if(isset($APP_TVScrobble) && $APP_TVScrobble==1) { echo "selected";} else{if($conf->enable_tvshow_scrobbling==1){ echo "selected"; }}?> value="1">Yes</option> 
	<option <?php if(isset($APP_TVScrobble) && $APP_TVScrobble==0) { echo "selected";} else{if($conf->enable_tvshow_scrobbling==0){ echo "selected"; }}?> value="0">No</option> 
  </select>
  
  <br />  <br />
  
  <label for="APP_FilmScrobble">Film scrobble:</label>
  <select id="APP_FilmScrobble" name="APP_FilmScrobble">
  	<option <?php if(isset($APP_FilmScrobble) && $APP_FilmScrobble==1) { echo "selected";} else{if($conf->enable_movie_scrobbling==1){ echo "selected"; }}?> value="1">Yes</option> 
	<option <?php if(isset($APP_FilmScrobble) && $APP_FilmScrobble==0) { echo "selected";} else{if($conf->enable_movie_scrobbling==0){ echo "selected"; }}?> value="0">No</option> 
  </select>  

  <?php if (DEBUG) { ?>  
  <br />  <br />
  <label for="APP_LogFile">Log File:</label>
  <input type="text" name="APP_LogFile" id="APP_LogFile" value="<?php  if(isset($APP_LogFile)){ print $APP_LogFile; }else{echo $conf->log_file;}?>" />
  <?php } ?>
  <br />
  
  </fieldset>

  <p style="centering">
    <input type="submit" name="Submit" value="Submit" class="button" />
  </p>

</form> 

</body>
</html>
