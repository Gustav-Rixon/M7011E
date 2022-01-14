## M7011E, Design of Dynamic Web Systems, Lp2, H21 - Group DROP TABLES

This project was made for [M7011E "Design of Dynamic Web Systems"](https://www.ltu.se/edu/course/M70/M7011E/M7011E-Design-av-dynamiska-webbsystem-1.68712?kursView=kursplan&l=en), running over LP2-2021 at LTU.

## Table of Contents:

-  [Installation](#installation)
-  [Usage](#usage)
-  [Documentation](#documentation)
-  [License](#license)


## Installation

### Prerequisites
  [Python 3.8.12](https://www.python.org/) or later
  
  [MySQL](https://www.mysql.com/)
  
  [React](https://reactjs.org/)

### Run
  * `git clone https://github.com/Gustav-Rixon/M7011E`
  
  * `pip install requirements.txt`
  
  Setup MySQL database from our database schema [ADD FILE NAME]
  
  Configure configuration.json in conf with your database credentials. You can also change the keys for the JWT tokens which we recommend. 
  
## Usage

From /../M7011E run python .\main.py


## Documentation

Documentation is located in docs.

From docs run `sphinx-apidoc -o . ..`

Then view index.html from you favorite web browsers.

## License

The program is-licensed under the MIT license.
