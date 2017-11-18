# Item Catalog

Flask application to view and make changes to a database when appropriate credentials are provided.

_Created in partial fulfillment of Udacity's Full Stack Web Developer Nanodegree_

## Requirements
* [Python3.x](https://www.python.org/)
* [Vagrant](https://www.vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/)

## Project Files
* views.py - main executable Python script; creates website on localhost:5000 displaying database information
* client_secrets.json - application client secrets
* sample_catalog.py - creates a catalog for testing
* catalog.db - tester catalog created by sample_catalog.py
* styles.css - main css file for website aesthetics (adapted from [Udacity](https://github.com/udacity/ud330))
* templates - html template files for website

## Setup
1. Install all required programs.
2. Clone OR download [VM](https://github.com/udacity/fullstack-nanodegree-vm) repository.
3. Download and unzip [data](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip) into the Vagrant directory.
4. Clone this repository OR download and unzip the project file into Vagrant directory.

## Running the Project
1. In the command-line interface, launch the Vagrant VM from inside the Vagrant directory using:

`$ vagrant up`

`$ vagrant ssh`

2. Change directory to /vagrant.
3. Load the data using:

`$ python sample_catalog.py`

4. Run the flask application using:

`$ python views.py`

5. Open localhost:5000 in web browser of choice
