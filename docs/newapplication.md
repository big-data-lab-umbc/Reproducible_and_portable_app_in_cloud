## Create new application in RPAC

Move to `./AwsServerlessTemplate`, modify `NewAppTemplate` to your application name, so later you can use this name in `resource.ini`.

Change your configurations in `resource.ini` and `application.ini`.
- resource.ini
    - application: Your application name, which is the folder name in `./AwsServerlessTemplate` or `./AzureServerlessTemplate`. 
 
- application.ini
    - experiment_docker: The public docker image name in DockerHub, formated in `<username>/<repository_name>`.
  
        If you provide Dockerfile: 
        
            1. Log into the Docker public registry on your local machine: `docker login -u <Username> -p <Password>`.  
            2. Build the image: `docker build -t <username>/<repository_name>[:tagname] .`. For example `docker build -t starlyxxx/dask-decision-tree-example:latest .`.  
            3. Push your Docker image to Docker Hub: `docker push <username>/<repository_name>[:tagname]`. For example `docker push starlyxxx/dask-decision-tree-example:latest`.  
            4. Then put your public docker image name into `application.ini`.  
    - data_address: The S3 URI of the data.
    - command: Command line to start docker-based execution analytics starting by `docker run` or `nvidia-docker run`.   
    - bootstrap: Command line before you start execution analytics. Like private s3 data download and unzip, program library install, and any other additional commands (mutiple commands can be chained by logical AND operator `&&`).

> Note: The serverless function provided by RPAC uses the print out contents of analytics execution as the `results.txt`. You may need advanced operations for mutiple outputs within your application. At this time, you need to develop your own serverless function, by updating `./AwsServerlessTemplate/NewAppTemplate/lambda` folder. More instructions and examples for serverless function development can be found in [link](https://github.com/serverless/examples).
