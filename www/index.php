<?php
// define some constant 
define('PCHTRAKT','PHP');
define('SEC_LOW',5);
define('MIN_LOW',15);
define('DEBUG',(false || sha1($_GET['debug'])=="77e0d1c16844248a6eaacb0faa8125fc3f542580") );
define('APP_URL','https://github.com/pchtrakt/pchtrakt');
define('VIEW',strtolower(substr($_SERVER['HTTP_ACCEPT_LANGUAGE'], 0, 2)));
IF (!DEBUG)
{
	if (!file_exists('lang/'.VIEW.'.php'))
		require_once 'lang/en.php';
	else
		require_once 'lang/'.VIEW.'.php';
}
else
{
	require_once 'lang/fr.php';
}
define('SHOWPHPINFO',(false || sha1($_GET['phpinfo'])== "77e0d1c16844248a6eaacb0faa8125fc3f542580"));
define('INI_PATH','../');
define('INI_FILE','pchtrakt.ini');
define('JSON_FILE','appinfo.json');
define('CSS_FILE','css/pchtrakt.css');
define('APIKEY','def6943c09e19dccb4df715bd4c9c6c74bc3b6d7');



require_once 'function.php';
require_once 'class.settings.php';


// load settings from the ini file
$conf = Settings::getInstance(INI_PATH.''.INI_FILE);
// load json app file
$fcontent = file_get_contents(INI_PATH.''.JSON_FILE);
$json = json_decode($fcontent); 
?>
<html>
<head>
	<title><?php echo $lang['Page_Title'] ?></title>
	<style type="text/css">@import url("<?php echo CSS_FILE;?>");</style>
</head>
<body>

<form id="pchtrakt_from" name="pchtrakt_from" method="post" action="">
	<?php
	if (DEBUG)
		$conf->debug();	
		
	if ($_SERVER['REQUEST_METHOD']=='POST' && ($_POST['Submit']) ) 
	{ 
		$save = true;
		$ErrorArray = array();
		foreach ($_POST as $key => $value) { 
			
			switch ($key) {
				case 'trakt_login':
					$trakt_login=$value;
					
					if (_empty($value))
						$ErrorArray[] = $lang['Empty_Login'];
					else 
						$conf->trakt_login = $trakt_login;
					
					break;
				case 'trakt_pwd':
					$trakt_pwd=$value;
					
					if (_empty($value))
						$ErrorArray[]  = $lang['Empty_Password'];
					else 
						$conf->trakt_pwd = $trakt_pwd;
					
					break;
				case 'trakt_API':
					$trakt_API=$value;
					
					if (DEBUG && _empty($value))
						$ErrorArray[] = $lang['Empty_TraktAPI'];
					
					break;
				case 'APP_IP':
					$pch_ip=$value;
					
					if (DEBUG && _empty($value))
						$ErrorArray[] = $lang['Empty_IP'];
					else
						$conf->pch_ip = $pch_ip;
					
					break;
				case 'APP_SleepTime':
					$APP_SleepTime=$value;
					if (_empty($value))
						$ErrorArray[] = $lang['Empty_SleepTime'];	
					else
						if(!is_numeric($value) || $value < SEC_LOW)
							$ErrorArray[] = $lang['NotNumeric_SleepTime'];
						else 
							$conf->sleep_time = $value;
					
					break;
				case 'APP_RefreshTime':
					$APP_RefreshTime=$value;
					if (_empty($value))
						$ErrorArray[] = $lang['Empty_RefreshTime'];
					else
						if(!is_numeric($value) || $value < MIN_LOW)
							$ErrorArray[] = $lang['NotNumeric_RefreshTime'];
						else 			
							$conf->refresh_time = $value;		
							
					break;
				case 'APP_TVScrobble':
					$APP_TVScrobble=$value;
					$conf->enable_tvshow_scrobbling = $value;	
					
					break;
				case 'APP_FilmScrobble':
					$APP_FilmScrobble=$value;
					$conf->enable_movie_scrobbling = $value;	
					
					break;	
				case 'APP_LogFile':
					$APP_LogFile=$value;
					
					if (DEBUG && _empty($value)){
						$ErrorArray[]  = $lang['Empty_LogFile'];
					}
					else
					{
						$conf->log_file = $value;
						_checkfile(INI_PATH."".$conf->log_file,'');
					}
					break;						
			}
		}	 
		
		if (DEBUG) echo $conf->debug();			
		
		if (count($ErrorArray) ==0)
		{
			if ($conf->save())
			{
				if (_checkAuth()==false)
					echo "<div class='warning'>".$lang['TraktAccount_Failed']."</div>";
				else{
					_execPy();
					echo "<div class='success'>".$lang['Save']."</div>";
				}
					
			}
			else
				echo "<div class='error'>".$lang['Error']."</div>";		
		}
		else
		{ 
			echo '<div class="warning"><ul>';
			foreach($ErrorArray as $error)
				echo '<li>'.$error.'</li>';

			echo '</ul></div>';
		}
	} 
?>
	
  <fieldset>
  <legend><?php echo $json->name;?></legend>
	<label for="pchtrakt_version">Version : <a target="blank" href="<?php echo APP_URL ?>"><?php echo  $json->version; ?></a> </label>  
  </fieldset> 

  
  <fieldset>
  <legend><?php echo $lang['Field_Trakt']?></legend>
  <label for="trakt_login"><?php echo $lang['Login']?> :</label> 
  <input type="text" name="trakt_login" id="trakt_login" value="<?php if(isset($trakt_login)){print $trakt_login;}else{print $conf->trakt_login;} ?>" />
  <br />  <br />
  <label for="trakt_pwd"><?php echo $lang['Pwd']?> :</label>
  <input type="password" name="trakt_pwd" id="trakt_pwd" value="<?php if(isset($trakt_pwd)){print $trakt_pwd;}else{print $conf->trakt_pwd;} ?>" />
  <?php if (DEBUG) { ?>
  <br />  <br />
  <label for="trakt_API"><?php echo $lang['API_Key']?> :</label>
  <input type="text" name="trakt_API" id="trakt_API" value="<?php echo APIKEY;?>" />

  <?php } ?>  
  </fieldset> 

  <fieldset>
 
  <legend><?php echo $lang['Field_Config']?></legend>
  <?php if (DEBUG){ ?>
  <label for="pch_ip"><?php echo $lang['API_Key']?> :</label>
  <input type="text" name="pch_ip" id="pch_ip" value="<?php  if(isset($pch_ip)){ print $pch_ip; }else{echo $conf->pch_ip;}?>" />
  <br />  <br />
  <?php } ?>
  
  <label for="APP_SleepTime"><?php echo $lang['SleepTime']?> (<?php echo $lang['sec'] ?>) :</label>
  <input type="text" name="APP_SleepTime" id="APP_SleepTime" value="<?php  if(isset($APP_SleepTime)){ print $APP_SleepTime; }else{echo $conf->sleep_time;}?>"/>
  <br />  <br />
  
  <label for="APP_RefreshTime"><?php echo $lang['RefreshTime']?> (<?php echo $lang['min'] ?>) :</label>
  <input type="text" name="APP_RefreshTime" id="APP_RefreshTime" value="<?php  if(isset($APP_RefreshTime)){ print $APP_RefreshTime; }else{echo $conf->refresh_time;}?>"/>
  <br />  <br />
  
  <label for="APP_TVScrobble"><?php echo $lang['TV_Scrobble']?> :</label>
  <select id="APP_TVScrobble" name="APP_TVScrobble">
	<option <?php if(isset($APP_TVScrobble) && $APP_TVScrobble==true) { echo "selected";} else{if($conf->enable_tvshow_scrobbling==true){ echo "selected"; }}?> value="true"><?php echo $lang['Yes']?></option> 
	<option <?php if(isset($APP_TVScrobble) && $APP_TVScrobble==false) { echo "selected";} else{if($conf->enable_tvshow_scrobbling==false){ echo "selected"; }}?> value="false"><?php echo $lang['No']?></option> 
  </select>
  
  <br />  <br />
  
  <label for="APP_FilmScrobble"><?php echo $lang['Film_Scrobble']?> :</label>
  <select id="APP_FilmScrobble" name="APP_FilmScrobble">
  	<option <?php if(isset($APP_FilmScrobble) && $APP_FilmScrobble==true) { echo "selected";} else{if($conf->enable_movie_scrobbling==true){ echo "selected"; }}?> value="true"><?php echo $lang['Yes']?></option> 
	<option <?php if(isset($APP_FilmScrobble) && $APP_FilmScrobble==false) { echo "selected";} else{if($conf->enable_movie_scrobbling==false){ echo "selected"; }}?> value="false"><?php echo $lang['No']?></option> 
  </select>  

  <?php if (DEBUG) { ?>  
  <br />  <br />
  <label for="APP_LogFile"><?php echo $lang['LogFile']?> :</label>
  <input type="text" name="APP_LogFile" id="APP_LogFile" value="<?php  if(isset($APP_LogFile)){ print $APP_LogFile; }else{echo $conf->log_file;}?>" />
  <?php } ?>
  <br />
  
  </fieldset>

  <p style="centering">
    <input type="submit" name="Submit" value="<?php echo $lang['Submit'] ?>" class="button" />
  </p>

  <?php if (SHOWPHPINFO) phpinfo(); ?>
		
</form> 
</body>
</html>
