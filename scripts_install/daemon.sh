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
   rm -r /share/Apps/PCHtrakt
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

# install PCHtrakt
#verif version?
 if [ -d /share/Apps/PCHtrakt/lib ] ; then
   echo "PCHtrakt is installed"
   else
   chmod 777 /share/Apps/PCHtrakt
   mkdir /share/tmp
   cd /share/tmp
   git clone -b dvp git://github.com/PCHtrakt/PCHtrakt.git
  #git clone git://github.com/PCHtrakt/PCHtrakt.git PCHtrakt
   cp -R PCHtrakt/* /share/Apps/PCHtrakt
   chmod 777 /share/Apps/PCHtrakt
   cd
   rm -r /share/tmp
 fi
}

force_PCHtrakt()
{
   chmod 777 /share/Apps/PCHtrakt
   cd /share/Apps/PCHtrakt
   #rm -r /share/Apps/PCHtrakt/daemon.sh
   #wget www.jamied.pwp.blueyonder.co.uk/SBC200/daemon.sh
   mkdir /share/tmp
   cd /share/tmp
   git clone -b dvp git://github.com/PCHtrakt/PCHtrakt.git
   #git clone git://github.com/PCHtrakt/PCHtrakt.git PCHtrakt
   cp -R PCHtrakt/* /share/Apps/PCHtrakt
   chmod -R 777 /share/Apps/PCHtrakt
   cd
   rm -r /share/tmp
}

force_all()
{
opkg update
opkg install python2.7-dev -force-depends -force-overwrite
opkg install git -force-depends -force-overwrite
cd /share/Apps/PCHtrakt/
}

start_PCHtrakt()
{
# start PCHtrakt
ps | grep "PCHtrakt.py" > /dev/null
if [ $? -ne 0 ];
then
echo "PCHtrakt.py is not running, Starting processes"
python2.7 /share/Apps/PCHtrakt/PCHtrakt.py --daemon > /dev/null 2>&1
fi
}

stop_PCHtrakt()
{
# Stop PCHtrakt
kill $(ps -ef |grep "PCHtrakt" |awk '{ print $1 }') > /dev/null 2>&1

}

#Main
case "$1" in
    start)
    install_defaults;
    ;;


    stop)
    stop_PCHtrakt;
    exit
    ;;

    restart)
    stop_PCHtrakt;
    sleep 2
    start_PCHtrakt;
    ;;

    forceall)
    stop_PCHtrakt;
    sleep 2
        force_all;
    force_PCHtrakt;
    sleep 2
        start_PCHtrakt;
    ;;

    forcesb)
    stop_PCHtrakt;
    sleep 2
        force_PCHtrakt;
    sleep 2
        start_PCHtrakt;
    ;;
esac
