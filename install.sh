#!/bin/bash
#
# SCRIPT TO INSTALL A WORDPRESS INSTANCE WITHIN A BIBBOX SERVER
#
#
echo "Installing Molgenis BIBBOX Application"
echo "installing from $PWD"

PROGNAME=$(basename $0)

error_exit()
{
	echo "ERROR in ${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
	clean_up 1
}

 #ADD CUSTOM CHECKS AN LOSs as YOU LIKE
checkParametersAndWriteLog() 
{
    echo "Setup parameters:"
    echo "MYSQL admin passwort: $MOLGENIS_ADMIN_PASSWORD"
    echo "MYSQL admin e-mail:   $MOLGENIS_ADMIN_EMAIL"
    echo "MYSQL root password:   $MYSQL_ROOT_PASSWORD"
    echo "MYSQL password for user molgenis:   $MYSQL_PASSWORD"
}

updateConfigurationFile()
{
    echo "Create and Update config files"  
    if  [[ ! -f "$folder/docker-compose.yml" ]]; then
        cp docker-compose-template.yml "$folder/docker-compose.yml"
    fi
  # SAME IN EVERY INSTALL.SH / DONT CHANGE  
    sed -i  "s/§§INSTANCE/${instance}/g" "$folder/docker-compose.yml"
    sed -i  "s#§§FOLDER#${folder}#g" "$folder/docker-compose.yml"
    sed -i  "s/§§PORT/${port}/g" "$folder/docker-compose.yml"
  # CHANGE  
  # TODO special characters in passwords 
    sed -i "s#§§MOLGENIS_ADMIN_PASSWORD#${MOLGENIS_ADMIN_PASSWORD}#g" "$folder/docker-compose.yml"
    sed -i "s#§§MOLGENIS_ADMIN_EMAIL#${MOLGENIS_ADMIN_EMAIL}#g" "$folder/docker-compose.yml"
    sed -i "s#§§MYSQL_ROOT_PASSWORD#${MYSQL_ROOT_PASSWORD}#g" "$folder/docker-compose.yml"
    sed -i "s#§§MYSQL_PASSWORD#${MYSQL_PASSWORD}#g" "$folder/docker-compose.yml"
}

createFolders()
{
    echo "Create folders within $folder"
    if [[ ! -d "$folder" ]]; then
        echo "Creating Installation Folder"
        mkdir -p "$folder/var/lib/mysql"
    fi
}

#
# MAIN
while [ "$1" != "" ]; do
    case $1 in
        -i | --instance )       shift
                                instance=$1
                                ;;
        -f | --folder )         shift
                                folder=$1
                                ;;
        -p | --port )           shift
                                port=$1
                                ;;
        --MOLGENIS_ADMIN_PASSWORD ) shift
                                MOLGENIS_ADMIN_PASSWORD=$1
                                ;;
        --MOLGENIS_ADMIN_EMAIL )      shift
                                MOLGENIS_ADMIN_EMAIL=$1
                                ;;
        --MYSQL_ROOT_PASSWORD )          shift
                                MYSQL_ROOT_PASSWORD=$1
                                ;;   
        --MYSQL_PASSWORD )      shift
                                MYSQL_PASSWORD=$1
                                ;;
    esac
    shift
done


# SAME IN EVERY INSTALL.SH / DONT CHANGE
checkParametersAndWriteLog
createFolders
updateConfigurationFile
