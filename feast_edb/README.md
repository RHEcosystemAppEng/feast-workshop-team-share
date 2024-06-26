## Configuring enterprise database on Openshift.

Go to openshift instance. We have to install the edb operator to setup enterprise database.

Go to Operators --> OperatorHub --> Search for the keyword "edb"
![EDB operator](./images/1-operators-search.png)
Select the EDB Postgres for Kubernetes to install the regular EDB postgres cluster. We have installed the version 1.22.3 without any issues.
![install the EDB Operator](./images/2-EDB-postgres-for-k8s.png)
You can check if the operator is installed under installed operators menu item.
![installed operators](./images/3-installed-operators.png)
Open the installed edb operator --> navigate to cluster tab.
![Cluster tab](./images/4-operator-cluster.png)
Click on create cluster tab for creating new cluster and provide all the details as per your scenario.
![create-a-cluster](./images/5-create-edb-cluster.png)
Open the cluster tab on the operator to see list of available clusters and their statuses.
![Clusters list](./images/6-cluster-list-after-creation.png)
Also you can check the statuses of newly created pods and all those should be in running state if everything initializes properly.
![Clusters-pods](./images/7-edb-pods-list.png)

Now the enterprise database has provisioned successfully. Please use below commands to connect to database from your local machine.

#### Port forwarding with openshift to access edb database
You can pick any pod name. in my case pod name is feast-edb-cluster-1
```shell
oc port-forward pod/<pod_name> 5432

oc port-forward pod/feast-edb-cluster-1 5432
Forwarding from 127.0.0.1:5432 -> 5432
Forwarding from [::1]:5432 -> 5432
```

## Configuring the Enterprise Database as feast registry
As part of this tutorial going to demonstrate how to configure enterprise database which we created in previous step as feast registry store.

If you have not already set up the feast on your local machine then use below command
```shell
# Installing feast using pip.
pip install feast
```

Create the new feast repo based on the postgres template using below command. You need the password to connect to database as part of this step.
You can refer the kubernetes secrets to get the password to access database cluster. In my case k8 secret is named as `feast-edb-cluster-app`  
```shell
> feast init -t postgres feast_edb_repo

Postgres host [localhost]: 
Postgres port [5432]: 
Postgres DB name [postgres]: app
Postgres schema [public]: public
Postgres user: app
Postgres password: 
Should I upload example data to Postgres (overwriting "feast_driver_hourly_stats" table)? [Y/n]: Y

Creating a new Feast repository in /Users/<>/feast_edb_repo.
> cd feast_edb_repo
> tree .
.
├── __init__.py
└── feature_repo
    ├── __init__.py
    ├── __pycache__
    │   ├── __init__.cpython-311.pyc
    │   └── test_workflow.cpython-311-pytest-7.4.4.pyc
    ├── example_repo.py
    ├── feature_store.yaml
    └── test_workflow.py
```
Open the default feature store configuration file if everything looks good.
> cat feature_repo/feature_store.yaml
```yaml
project: feast_edb_repo
provider: local
registry:
    registry_type: sql
    path: postgresql://postgres:mysecretpassword@127.0.0.1:55001/feast
    cache_ttl_seconds: 60
    sqlalchemy_config_kwargs:
        echo: false
        pool_pre_ping: true
online_store:
    type: postgres
    host: localhost
    port: 5432
    database: app
    db_schema: public
    user: app
    password: mysecretpassword
offline_store:
    type: postgres
    host: localhost
    port: 5432
    database: app
    db_schema: public
    user: app
    password: mysecretpassword
entity_key_serialization_version: 2
```
You have to update the above configuration to keep edb database as the registry as well with below configuration.
```yaml
project: feast_edb_repo
provider: local
registry:
  registry_type: sql
  path: postgresql://app:mysecretpassword@127.0.0.1:5432/app
  cache_ttl_seconds: 60
  sqlalchemy_config_kwargs:
    echo: true
    pool_pre_ping: true
online_store:
    type: postgres
    host: localhost
    port: 5432
    database: app
    db_schema: public
    user: app
    password: mysecretpassword
offline_store:
    type: postgres
    host: localhost
    port: 5432
    database: app
    db_schema: public
    user: app
    password: mysecretpassword
entity_key_serialization_version: 2
```
Review all the configurations and if everything looks good then execute `feast apply`

```shell
> feast apply
..
..
..
Deploying infrastructure for driver_hourly_stats
Deploying infrastructure for driver_hourly_stats_fresh
```

Now your feast repo should be initialized successfully and all the required tables should be created in the provided schema.
In my case using dbeaver client, however, you can use any client.
![](./images/8-edb-schema-after-feast-apply.png)