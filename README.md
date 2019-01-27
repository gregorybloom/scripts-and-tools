Scripts and Tools
============
**FULL SCRIPTS**
- 111 Shutdown - server shutdown script.  Logs event to a file and attempts an email
- Autobackup - script to use pre-made config files to backup folders.  It can validate MD5s or email a summary.
- Backup 1xx - pull server data to archive.  This includes saving config files and dumping Mongo DB tables
- Base Dump Script - base script to organize automated backups, logs, and execution of other scripts.  Executed by tiny 'launcher' scripts for quick handling.
- Bash Wizardry - dumb file to play with shorthand bash.  For bash learning
- Deploy - script to deploy a web project to the server.  Uses text configs to ignore certain folder names.
- DiscordExporter - leverages another project to automate Discord log saving, packing, and synchronizing with previous logs
- TxtList to DatList - concats and converts files in tmp/ into a ip blocklist
- TestCheck - python script testing various hashing methods

**Hero DB Builder**
Series of python scripts and templates to parse an old site database.

**IN PROGRESS**
- BuddyExporter - exports SessionBuddy data directly from Chrome's folders.  Saves it in a 'Backups' folder.
- Find Dupes - quick script to take the python 'md5/sha' logs format used in raidcheck and other scripts and find duplicates
- FixDosEnds - purges the windows-specific file ends from project files.  Doesn't always work?

**DEFUNCT?**
- Push SiteConf 100 - push last 'config dump' backup onto server
- Pull 100 PythonData - pulls data from (defunct) python project
- Retrieve - copies a path from the server to local computer
- LogCheck?
