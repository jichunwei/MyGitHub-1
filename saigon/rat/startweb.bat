@echo off
set dbname=%1
if /i "%dbname%" == "" (goto :default_rat_db)

set RAT_DB_NAME=%dbname%
goto :startup_web

:default_rat_db
set RAT_DB_NAME=rat.db

:startup_web
echo "RAT DATABASE_NAME is %RAT_DB_NAME%"
manage.py runserver 0.0.0.0:8009
pause