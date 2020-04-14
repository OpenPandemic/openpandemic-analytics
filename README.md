<p align="center">
  <a href="http://www.openpandemic.io"><img alt="openpandemic" src="https://avatars2.githubusercontent.com/u/63398478?s=100&v=4" width=100 /></a>
  <h3 align="center">Openpandemic App - Analytics</h3>
  <p align="center">
    <img align="center" alt="We love Opensource" src="https://badges.frapsoft.com/os/v1/open-source.svg?v=103" />
    <img align="center" alt="License check" src="https://app.fossa.io/api/projects/git%2Bgithub.com%2Fopenpandemic%2Fopenpandemic-analytics.svg?type=shield" />
  </p>
</p>

---

This is an opensource initiative to analyze pandemic diseases, such as coronavirus (COVID-19) for example. It's a complementary project of [openpandemic-app](https://github.com/OpenPandemic/openpandemic-app) and [openpandemic-back](https://github.com/OpenPandemic/openpandemic-back).

Whenever we can, we will use containers for all the functionality, thus ensuring reproducibility in any environment.

## Requirerements:

- Make (gcc).
- Docker (17+).
- Google Cloud Platform (GCP) project access.
- Python 3.8 (pipenv)

## Get starting with GCP

We need to have a GCP project and all needed APIs enabled beforehand.

You could use the official gcloud command client as you know, but we encourage you to use it within docker containers.

To authenticate with GCP credentials create a `.env` file with the reserved environment variables and set up the suitable values:

```bash
GOOGLE_CLOUD_PROJECT="openpandemic-analytics"
GOOGLE_APPLICATION_CREDENTIALS="<path>/openpandemic-analytics.json"
```

Now we can run a docker container which is authenticated to get bq command client ready for action:

````bash
make gcloud-bastion
```` 

Now you can use the shell through the container (type `make bq-`+tab to discover more aliases):

````bash
make bq-shell
```` 


## Data 

In order to use the data provided by the project `openpandemic-back`, you need to get access to the BigQuery tables (unless these tables are public)

### Generate test data

A lot of times we need data to get start with analytics task, so we could use synthetic data (not always), for this reason we've add a Faker provider to generate table entries from evaluations.

For example, to generate `fake data` for covid19 symptoms evaluations type next command:

```bash
pipenv run python -m openpandemic.fake.fake_data
```

The output of that command execution is a `data/ES/fake_data_es_v1.json`, regarding the Bigquery data schema `data/bq_data_schema_v1.json`


#### Load data to Bigquery

You could upload generated data to Bigquery, just use the suitable command or use the humble script:

```bash
pipenv run python -m openpandemic.bq.load_fake_data

Loading .env environment variables...
2020-04-14 01:09:26,295 - openpandemic [load_fake_data.py:19] - INFO - Created dataset openpandemic-analytics.openpandemic_test
2020-04-14 01:09:26,561 - openpandemic [load_fake_data.py:35] - INFO - Table openpandemic-analytics.openpandemic_test.data_test_es_v1 was recreated.
2020-04-14 01:09:26,729 - openpandemic [load_fake_data.py:39] - INFO - Created table: /projects/openpandemic-analytics/datasets/openpandemic_test/tables/data_test_es_v1
2020-04-14 01:09:30,469 - openpandemic [load_fake_data.py:57] - INFO - Loaded 5000 rows.
```

or by using command client:
````bash
make bq-create-dataset bq-create-table bq-upload-data
````

## Notebooks

Take a look at our [notebooks section](notebooks) to get more information.

## Dashboard information

We've created a Data Studio report to outline the most interesting information about pandemics.

![Google Data Studio Report](img/datastudio.png)

## AI

[Work in progress]

## Cleaning

Remove all resources:

```bash
make clean-clean
```
