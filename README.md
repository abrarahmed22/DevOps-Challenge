# DevOps-Challenge
## Part I - Github API & Pipedrive API

It is a gist scanner web service for fetching gists from multiple users using Github API and then create activity to a pipedrive sandbox via the Pipedrive API.

Ths stack used: Python, Github API, Pipedrive API, Flask, gunicorn, Docker, Jenkins, AWS

The main function of the scanner was implemented in the file  `github_api.py`

A web endpoint was created using Flask with gunicorn. For global access app is running on `http://13.38.226.102:8000/`.For localhost, the root link `http://localhost:8000/` will display the simplified gists fetched during the last run.
Since the original gists contain many data which are not neccessary, only 3 attributes are being kept here which are the name of the gist's owner, the url of the gist and the last updated time. An endpoint `http://13.38.226.102:8000/users` was also created for dispaying the names of the users being scanned

# Configuration
### gist users
The list of user being scanned is stored in the file `devOps_challenge.db`.

### scheduler
The scanner can be schedulled with second, hour and day. These could be configured in the config.py. After setting up the scheduler, the scanner will run with the time interval and scan all the gists updated or created since the last run. For instance, if the scheduler is set to run every 3 hours, the gists created or updated within last 3 hours will be fetched and activities will be created in pipedrive.

### pipedrive account
The api-key and the domain for pipedrive API could be edited in the config.py.

# How to run
### Option 1) Local build docker image and run
1, Clone this repo, in command prompt goto the directory of this project (optional: change the configurations in the config.py)

2, In command prompt, run `docker build  -t devops_challenge .`. Then a docker image should be built successfully.

3, In command prompt run `docker run -p 8000:8000 devops_challenge`.

The scanner and the web server should start and the log of the scanner will be displayed in command prompt. Browse http://localhost:8000/ and http://localhost:8000/users to see the fetched simplified gists and scanend users. login to pipedrive andd check if the activities have been created.

### Option 2) Pull docker image and run
1, In command prompt, run docker pull 1abrarahmed/devops_challenge
2, In command prompt, run `docker run -p 8000:8000 --name gistAppContainer 1abrarahmed/devops_challenge`  This will run the docker image that I have uploaded to the Docker Hub. It is configured to create activity to my sandbox in pipedrive and the scheduler is set to have 3 hours interval

## Part II - CI /CD

I used Jenkins to set up CI/CD process. Jenkins job bulid checks github actions get triggered by every commit pushed to main. 
it will also automatically build an image of the app and tag it if all the previous checks passed. the docker images will be deployed to the docker hub containers registry. project id and service account are defined in repo secrets to ensure the security of the key and ease of changing the project id or the service key without updating the code



## Part III - The cloud
For running the checks on user gists I didn't have to use any ops related solution, but I used python built-in schedulers. a function that would get all users and then fetch their gists then make activities in Pipedrive every 3 hours.

The docker image is following the builder pattern where we build on one container then run from another container. that allows us not to have to store our code on the customer facing container.

App is running on AWS ubuntu server with the host `http://13.38.226.102:8000/`
