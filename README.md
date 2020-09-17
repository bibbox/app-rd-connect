# MOLGENIS BIBBOX application

## Hints
* approx. time with medium fast internet connection: **15 minutes**
* initial user/passwordd: **admin / '<'set during instalations'>'**

## Docker Images Used
 * [bibbox/molgenis](https://hub.docker.com/r/bibbox/molgenis/) 
 * [mySQL](https://hub.docker.com/_/mysql/), offical mySQL container
 * [busybox](https://hub.docker.com/_/busybox/), offical data container
 
## Install Environment Variables

## Mounted Volumes

* the mysql datafolder _/var/mysql_ will be mounted to _/opt/apps/INSTANCE_NAME/var/mysql_ in your BIBBOX kit 

## Biobank Explorer and Data Upload

* Use "Advanced Data Import" (in "Import Data") to upload/import the provided eu_bbmri_eric.xlsx file
* Use "App Manager" (in "Plugins") and upload/import the provided molgenis_app_biobank_explorer.zip
* Use "Menu Manager" (in "Admin"), create a new Menu item on the top right by choosing the app_molgenis_biobank_explorer and a custom name
* After creating the menu item, Drag and Drop it to the desired position in the Menu ("HOME" MUST BE FIRST!)

## Freemarker Template

* Go to "Data Explorer", choose Category "Freemarker Template" and add a new Row (green "Plus"-Symbol)
* Set the name to the name of the provided .ftl files (e.g.: view-entityreport-specific-eu_bbmri_eric_collections.ftl)
* copy the content of the .ftl file into "Value" ; Save
* go to Admin-Settings-DataExplorerSettings and link entity to the .ftl file (entity-name:template-name e.g.: collections:eu_bbmri_eric_collections)

