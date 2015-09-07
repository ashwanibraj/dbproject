# dbproject
Stock Analyzer

Pre-requisites:

1) Must have a gatorlink id and password(only available for University of Florida students and faculty)
  This is required to establish a VPN to UF server.

2) Must have python, Django installed

To run:
1) Download and open Cisco AnyConnect. Enter Gatorlink username and password to connect to Gatorlink VPN.

2) Open SQL Developer and connect to the UF Database server.

  i) Open Proj_DB_create.sql and execute all queries. This will create the database objects.
  
  ii) Load all tables with data. For historic stock data, refer to folder "Data for DB" or yahoo finance
  
2) Open terminal window and run command 

  i) "python manage.py inspectdb > finapp/models.py"
  
  ii) "python manage.py runserver"
  
3) Open a web browser and go to http://127.0.0.1:8000/finapp/

NOTE: Lookup the link http://www.oracle.com/webfolder/technetwork/tutorials/obe/db/oow10/python_django/python_django.htm

