# AWS Events Exporter

Utility for exporting favorite sessions from AWS events to an excel file.<br>
Specifically hard coded for AWS re:Invent 2022, but this can be changed.

## Pre-requisites

-   Python 3.8
-   [Poetry](https://python-poetry.org/docs/#installation)

## Usage

-   Open a terminal and run `poetry install` to create a python virtual environment and install all dependencies
-   Open a web browser and go to [https://portal.awsevents.com/events/reInvent2022/](https://portal.awsevents.com/events/reInvent2022/)

    -   Open you browser's dev tools
    -   Go to the storage tab
    -   Expand local storage and choose `https://portal.awsevents.com`
    -   Copy the value for `CognitoIdentityServiceProvider.<long string>.accessToken`

-   Create a new `.env` file in the repo dir, and add the following line:

```
AWS_EVENTS_ACCESS_TOKEN=<The value that you copied from the browser>
```
- Run within poetry virtualenv
```
poetry shell
```

-   Run the utility by executing the following command in a terminal window in the repo dir:

```
./favorites_exporter.py
```

-   A `favorites.xlsx` file will be created containing all of your favorite sessions
