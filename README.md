
# Nmap app

A humble dockerized solution that performs the port scans ACK, SYN, NULL, XMAS on the websites [here](http://www.vulnweb.com/),
stores it on 3 datastores and provides a simple dashboard with a table of the latest scan results.

Here are the different web applications and their roles:
  
  - owl : a python app that performs the scans and sends the output to ostrich
  - ostrich : a python app that receives results via an api layer and saves it to the 3 data stores
  - eagle : a nodejs app that displays a dashboard with a table of the latest scan results by pulling from the postgres datastore


some useful commands
    
   - basic setup
   ```
      sudo apt-get install python3.6-dev
      python3.6 -m venv .py3env
      source .py3env/bin/activate
   ```

   - run the entire docker setup
   ```
     ./build.sh
   ```
   
   - shutdown the entire docker setup
   ```
     ../shutdown.sh
   ```
     
   - to test
   ```
      ostrich (from root dir):
          . ./env_test && python -m unittest -v ostrich.test.test_db_helper
          . ./env_test && python -m unittest -v ostrich.test.test_app
        
      peacock (from peacock):
          npm test
   ```
        
   - to run peacock:
   ```
      cd peacock
      . ../env_test && npm start
   ```
   
   - to run owl:
   ```
      cd owl
      . ../env_test && flask run -p 5001 --host=0.0.0.0
   ```
   
   - to run ostrich:
   ```
      cd ostrich
      . ../env_test && flask run -p 6001 --host=0.0.0.0
   ```
        
   - to connect to redis:
   ```
      redis-cli -h localhost -p 6379 -a redis -n 0
   ```
   
   - to connect to postgres:
   ```
      psql -h localhost -U nmap_app nmap_scan
   ```


Improvements:

   - admin scripts to view the data within redis, postgres, rabbit
   - adding proper dependency tracking in [docker](https://github.com/jwilder/dockerize#waiting-for-other-dependencies)
   - use loggers instead of printlines
   - a better dashboard (peacock)
