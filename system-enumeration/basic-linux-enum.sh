#!/usr/bin/env bash
# very quick system enumeration
# Current username
password=$1
echo $password
echo -e "Username: $(whoami)"
echo -e "UID: $(whoami | id -u)"
echo -e "$(uname -a)"
printf "\n"
# Try to read the /etc/passwd file to enumerate usernames (usually it is readable)
echo "Usernames"
echo -e "$(cat /etc/passwd)"
printf "\n"
# List all the privileges user have access
echo "sudo"
echo -e "$(echo $password| sudo -S -l)"
printf "\n"
# List common binarie folders
echo "Binaries"
echo "/bin"
echo -e "$(ls -lasH /bin)"
printf "\n"
echo "/usr/bin"
echo -e "$(ls -lash /usr/bin)"
printf "\n"
## Also search for folders "bin" created by users
echo "Binaries folder"
# Search for folder that have at least execution permission for the owner and are called like bin
echo -e "$(find / -perm -100 -iname *bin* -type d 2>/dev/null)"
printf "\n"
# Get the list of files that can be executed by any user but with the privilege of the owner
echo "SUID Files"
echo -e "$(find / -perm -4000 2>/dev/null)"
printf "\n"
echo "Executable files writable by current user and owned by root"
#echo -e "$(find / -uid 0 -perm -120 2>/dev/null)"