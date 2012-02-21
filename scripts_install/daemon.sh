#!/bin/sh
#Set Paths
PATH=$PATH:/usr/local/bin:/share/Apps/local/bin:/share/Apps/local/libexec/git-core:/nmt/apps/bin;export PATH
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/bin:/share/Apps/local/lib;export LD_LIBRARY_PATH
MANPATH=$MANPATH:/usr/local/share/man:/share/Apps/local/share/man;export MANPATH

install_defaults()
{
# Check opkg installation
 if [ -d /share/Apps/local ]; then
   echo "Required dependency, opkg (local) is installed."
   else
   echo "Required dependency, opkg (local) is not installed, install it via C.S.I"
   rm -r /share/Apps/pchtrakt
   exit 0
 fi

# Update opkg installation
 if [ -f /share/Apps/local/lib/opkg/lists/c200local ]; then
   echo "opkg (local) has been updated but cant tell when last this was, new versions may still be available."
   else
   echo "Updating opkg (local)"
   opkg update
 fi

 # install python2.7-dev
 if [ -f /share/Apps/local/bin/python2.7-config ]; then
   echo "Required dependency, python-2.7-Dev is installed."
   else
   opkg install python2.7-dev -force-depends -force-overwrite
 fi

 # install git
 if [ -f "/share/Apps/local/bin/git" ] ; then
   echo "Required dependency, git is installed."
   else
   opkg install git -force-depends -force-overwrite
 fi

# install pchtrakt
#verif version?
 if [ -d /share/Apps/pchtrakt/lib ] ; then
   echo "pchtrakt is installed"
   else
   force_pchtrakt;
 fi

}

force_pchtrakt()
{
   chmod 777 /share/Apps/pchtrakt
   cd /share/Apps/pchtrakt
   mkdir /share/tmp
   cd /share/tmp
   git clone git://github.com/pchtrakt/pchtrakt.git pchtrakt
   cp -R pchtrakt/* /share/Apps/pchtrakt
   chmod -R 777 /share/Apps/pchtrakt
   cp -f /share/Apps/pchtrakt/scripts_install/appinfo.json /share/Apps/pchtrakt/
   cp -f /share/Apps/pchtrakt/scripts_install/daemon.sh /share/Apps/pchtrakt/
   cd
   rm -r /share/tmp
}

force_all()
{
opkg update
opkg install python2.7-dev -force-depends -force-overwrite
opkg install git -force-depends -force-overwrite
cd /share/Apps/pchtrakt/
}

start_pchtrakt()
{
# start pchtrakt
ps | grep "[p]chtrakt.py --daemon" > /dev/null
if [ $? -ne 0 ];
then
echo "pchtrakt.py is not running, Starting processes"
cd /share/Apps/pchtrakt
python2.7 pchtrakt.py --daemon
cd
fi
}

stop_pchtrakt()
{
# Stop pchtrakt
if [ -n "`ps | grep "pchtrakt" | grep -v "grep"`" ]; then
        kill -9 `pidof python2.7 pchtrakt.py` >/dev/null 2>/dev/null
        sleep 2
fi
}

link_webui()
{
    if [ -d "${LOCAL_DIR}/web" ];then
        cd ${LOCAL_DIR}/web
        for webui in `ls -1`
        do
            if [ ! -L /share/Apps/AppInit/websites/${webui}_web ];then
                ln -s ${LOCAL_DIR}/web/${webui} /share/Apps/AppInit/websites/${webui}_web
            fi
        done

    fi
}

#Main
case "$1" in
    start)
    install_defaults;
    sleep 2
	start_pchtrakt;
    link_webui
    ;;


    stop)
    stop_pchtrakt;
    exit
    ;;

    restart)
    stop_pchtrakt;
    sleep 2
    start_pchtrakt;
    ;;

    update)
    stop_pchtrakt;
    sleep 2
    force_pchtrakt;
    sleep 2
    start_pchtrakt;
    ;;
    
    forceall)
    stop_pchtrakt;
    sleep 2
        force_all;
    force_pchtrakt;
    sleep 2
        start_pchtrakt;
    ;;
esac
