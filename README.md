# Database Monitor

This script was created to monitor a **remote** PostgreSQL database. The need was noted when several team members performed various tasks, including long-term queries, showing instability for a few days, some of them caused by the mass inclusion of data by the remote client.

So I found it interesting to automate databse monitoring, making it easier for some team members who were working remotely in other cities or at home. Thus, allowing the creation of a report containing the history of database connections for future presentations.

### Features

* Check the status of the internet network;
* Check VPN routes;
* Check the database connection every 1 minute;
* Save all events to a log file;
* Tray icon showing current status of database.

### Installation

* Before you run `ìnstall.sh`, give it root permission - `sudo chmod +x install.sh`;
* And then run `install.sh`.

### Future Improvements

* Make generic monitoring for any database;
* Create graphical reports according to history
