# User Cleaner

<a href="https://codeclimate.com/github/CorchoForce/user-cleaner/maintainability"><img src="https://api.codeclimate.com/v1/badges/4d557edf5762792e521e/maintainability" /></a>

![demonstration](https://cdn.discordapp.com/attachments/539836343094870016/891721423893168198/unknown.png)

## Table of Contents

<!--ts-->

- [About](#about)
- [Requirements](#requirements)
- [Routes](#routes)
  - [FutureRanking](#futureranking)
  - [Ranking](#ranking)
  - [Companies](#companies)  
- [How to use](#how-to-use)
  - [Setting up](#setup)
- [Technologies](#technologies)
<!--te-->

## About

It is a backend built for ESGeasy project. The objective of this is to build a api containing the companies informations like ESG score, company name and company id to be used in the frontend.

## Requirements

To run this repository by yourself you will need to install python, and them install all the project [requirements](requirements.txt) or, alternatively, you can use docker to run the entire application (exposed in the port 5000 by default). We will show how to do it in the next step.

## Routes

For this api we have only three routes where the explanation is located bellow:

### FutureRanking

This route receives a sector string and a score type and returns the json containing the company id, name and score related to the esg metrics prediction results in the following format:

```json
{
  "company_id": "str", 
  "company_name": "str", 
  "score": "float64"
}
```

### Ranking

This route receives a sector string and a score type and returns the json containing the company id, name and score related to the last esg results in the following format:

```json
{
  "company_id": "str", 
  "company_name": "str", 
  "score": "float64"
}
```

### Companies

This route receives a company id and returns the evolution graph image of esg metrics for the company and the data related to it like name, region, country, etc, in the following format:

```json
{
  "data": {
    "company_id": "str", 
    "company_name": "str", 
    "score": "float64"
  },
  "image": "base64"
}
```

## How to use

### Setup

```bash
# Clone the backend repository
$ git clone <https://github.com/Hackganization/tbd-back>

# Access the backend directory
$ cd tbd-back/

# Run the docker-compose file 
$ docker-compose up --build

After that the api will be running in the port 5000.
```

![demonstration](https://cdn.discordapp.com/attachments/539836343094870016/891725648001900594/unknown.png)

## Technologies

- Python
- Docker
- Pandas
- Flask
