<html>
  <head>
    <title>opkg Web - Networked Media Tank</title>
    <style type="text/css">
    h1, h2 { font-family: Arial, Helvetica, sans-serif; color: #004; }

    table { font-family: Arial, Helvetica, sans-serif; font-size: 12px;border-top: 1px solid #eee; border-right: 1px solid #eee; width: 100%; }

    th, td { padding: 2px 4px; border-left: 1px solid #eee; border-bottom: 1px solid #eee; }

    table a { background: #ddd; color: #004; text-decoration: none; margin: 1px;
    padding: 2px 4px; font-family: Arial, Helvetica, sans-serif; font-size: 75%; }

    table a.ins { background: #dfd; border-left: 1px solid #cec; border-bottom: 1px solid #cec; }

    table a.upd { background: #ddf; border-left: 1px solid #cce; border-bottom: 1px solid #cce; }

    table a.del { background: #fdd; border-left: 1px solid #ecc; border-bottom: 1px solid #ecc; }
    </style>
  </head>

  <body>
    <h1>The opkg web</h1>
    <form method="GET">
    <table>
      <tbody>
        <tr>
	  <td>Sync packages</td>
	  <td>
            <input type="radio" name="updatedb" id="no" value="n" checked><label for="no">no</label>
            <input type="radio" name="updatedb" id="yes" value="y"><label for="yes">yes</label>
	  </td>
        </tr>
        <tr>
	  <td>Type:</td>
	  <td>
            <select name="typefilter">
              <option selected value="none">NONE</option>
              <option value="update">Updates</option>
              <option value="installed">Installed</option>
              <option value="not">Not installed</option>
            </select>
          </td>
        </tr>
        <tr>
	  <td>Filter</td>
	  <td><input type="text" name="namefilter"></td>
        </tr>
      </tbody>
    </table>
    <input type="submit" name="submit">&nbsp;<input type="reset">
    </form>
    <h2>Package list</h2>
    <table border="1" cellpadding="0" cellspacing="0">
      <tbody>
        <tr><th>Task</th><th>Package</th><th>Installed Version</th><th>Available Version</th><th>Comment</th><th>Delete</th></tr>
<?php
$updatedb = $_GET["updatedb"];
$typefilter = $_GET["typefilter"];
$namefilter = $_GET["namefilter"];
$task = $_GET["task"];
$package = $_GET["package"];
$submit = $_GET["submit"];
if ($submit == "")
    $submit = "Submit";
if ($typefilter == "")
    $typefilter = "none";
if ($updatedb == "y")
    $command = shell_exec("/share/Apps/local/bin/opkg update 2>&- 1>&-");
if ($task == "install") 
    $command = shell_exec("/share/Apps/local/bin/opkg --force-overwrite install ".$package." 2>&- 1>&-");
else if ($task == "update") 
    $command = shell_exec("/share/Apps/local/bin/opkg --force-overwrite upgrade ".$package." 2>&- 1>&-");
else if ($task == "delete") 
    $command = shell_exec("/share/Apps/local/bin/opkg --force-depends remove ".$package." 2>&- 1>&-");

if ($submit != "") {
    $command = "/share/Apps/local/bin/opkg list_installed 2>&-|grep -v 'terminated' 1> /tmp/install_list";
    $install_list = shell_exec($command);
    $install_data = file("/tmp/install_list");
    unlink("/tmp/install_list");

if ($namefilter == "")
    $command = "/share/Apps/local/bin/opkg list 2>&-|grep -v 'terminated' 1>/tmp/avail_list";
else
    $command = "/share/Apps/local/bin/opkg list 2>&-|grep -v 'terminated'|grep '".$namefilter."' 1>/tmp/avail_list";
    $avail_list = shell_exec($command);
    $avail_data = file("/tmp/avail_list");
    unlink("/tmp/avail_list");

    foreach ($avail_data as $data) {
    $pdata = explode(" - ",$data);
    $version_cmp = preg_grep("/^$pdata[0] /", $install_data);
    print("<tr>\n");
    $installed_ver=array_pop($version_cmp);
    $idata=array();
    $delete = "";
    $installed = "n";
    if(sizeof($installed_ver) > 0){
        $installed = "y";
        $idata=explode(" - ", $installed_ver);
        if (trim($pdata[1]) != trim($idata[1]))
            $task = "<a href='?task=update&amp;package=".$pdata[0]."' class='upd'>Update</a>";
        else 
            $task = "";
        $delete = "<a href='?task=delete&amp;package=".$pdata[0]."' class='del'>Delete</a>";
    }
    else
        $task = "<a href='?task=install&amp;package=".$pdata[0]."' class='ins'>Install</a>";
    $show=0;
    switch($typefilter) {
    case "none":
        $show=1;
        break;
    case "update":
        if ($installed == "y" && $pdata[1] != $idata[1])
            $show=1;
        break;
    case "installed":
        if ($installed == "y")
            $show=1;
        break;
    case "not":
        if ($installed != "y")
            $show=1;
        break;
    }
    if ($show == 1)
        print("<td>$task</td><td>$pdata[0]</td><td>$idata[1]</td><td>$pdata[1]</td><td>$pdata[2]</td><td>$delete</td>\n");
    }
}
?>
      </tbody>
    </table>
  </body>
</html>
