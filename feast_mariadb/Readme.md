# Integrating MariaDB with Feast

## Objective
Integrating MariaDB with Feast (Feature Store for Machine Learning) as a scalable registry database offers a sophisticated approach to managing machine learning features with high efficiency and reliability. This setup leverages MariaDB for the Feast registry, which holds metadata about feature tables, definitions, and other crucial information, while PostgreSQL is utilized for both the online and offline feature stores. This architecture allows for a robust, scalable, and flexible system capable of handling the complexities of feature management in machine learning workflows.

The exercise focuses on configuring MariaDB as the central registry in the Feast ecosystem, which is essential for maintaining the integrity and consistency of feature metadata across different environments and stages of the machine learning lifecycle. MariaDB's proven performance and scalability make it an excellent choice for supporting the dynamic and growing requirements of machine learning projects.

Additionally, the use of PostgreSQL for online and offline feature stores complements the setup by providing a powerful and reliable storage solution for actual feature values. This separation of concerns allows for optimized configurations tailored to the specific needs of metadata management and feature storage, ensuring efficient operations and high availability of data for training and serving machine learning models.

This guide will cover the necessary steps to integrate MariaDB with Feast, including setting up the scalable registry, configuring PostgreSQL as the feature store, and illustrating how to leverage these components for effective feature management. This integration strategy is ideal for organizations aiming to build scalable, high-performance machine learning systems that require precise control over feature data and metadata.

## Instructions
### Step 1. Install Postgres and MariaDB using Openshift Templates

a. Navigate to Openshift Console --> Developer's Tab
![openshift.png](openshift.png)

b. Click +Add and select Database (postgres ephemeral)
![postgres-db.png](postgres-db.png)

c. Instantiate template with your values
![template.png](template.png)

d. You should see both databases deployments
![deploy.png](deploy.png)

### Step 2: Create a feature repository(if creating new example repo) else SWITCH to STEP 3
```
feast init -t postgres feast_mariadb
```

### Step 3: Port-forward postgres and mariadb
```
oc port-forward pod/<pod_name> 5432
Forwarding from 127.0.0.1:5432 -> 5432
Forwarding from [::1]:5432 -> 5432
```

```
oc port-forward pod/<pod_name> 33306:3306 -n feast
Forwarding from 127.0.0.1:33306 -> 3306
Forwarding from [::1]:33306 -> 3306
```

### Step 4: Your `feature_store.yaml` file for local deployment -- 
```
project: feast_mariadb
provider: local
registry:
    registry_type: sql
    path: mysql://feast:feast@127.0.0.1:33306/sampledb
    cache_ttl_seconds: 60
online_store:
    type: postgres
    host: localhost
    port: 5432
    database: sampledb
    user: feast
    password: feast
offline_store:
    type: postgres
    host: localhost
    port: 5432
    database: sampledb
    user: feast
    password: feast    
entity_key_serialization_version: 2
```

Navigate to `/feast_mariadb/feature_repo` directory and do `feast_apply` -- 
If it complains about table not being found - create a table inside `postgres/mariadb` --
```
CREATE TABLE feast_driver_hourly_stats (
    ->    driver_id INT,
    ->    event_timestamp TIMESTAMP,
    ->    created TIMESTAMP,
    ->    conv_rate FLOAT,
    ->    acc_rate FLOAT,
    ->    avg_daily_trips INT
    -> );
```

Then `feast apply` --> you will see the following output -- 
```
(feast) ➜  feature_repo git:(mariadb) ✗ feast apply
zsh: /usr/local/bin/feast: bad interpreter: /usr/local/opt/python@3.11/bin/python3.11: no such file or directory
/opt/miniconda3/envs/feast/lib/python3.9/site-packages/feast/feature_store.py:565: RuntimeWarning: On demand feature view is an experimental feature. This API is stable, but the functionality does not scale well for offline retrieval
  warnings.warn(
/opt/miniconda3/envs/feast/lib/python3.9/site-packages/feast/infra/registry/sql.py:924: RemovedIn20Warning: Deprecated API features detected! These feature(s) are not compatible with SQLAlchemy 2.0. To prevent incompatible upgrades prior to updating applications, ensure requirements files are pinned to "sqlalchemy<2.0". Set environment variable SQLALCHEMY_WARN_20=1 to show all deprecation warnings.  Set environment variable SQLALCHEMY_SILENCE_UBER_WARNING=1 to silence this message. (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
  conn.execute(insert_stmt)
Deploying infrastructure for driver_hourly_stats
Deploying infrastructure for driver_hourly_stats_fresh
```

`feast feature-views list`
```
(feast) ➜  feature_repo git:(mariadb) ✗ feast feature-views list;
zsh: /usr/local/bin/feast: bad interpreter: /usr/local/opt/python@3.11/bin/python3.11: no such file or directory
NAME                         ENTITIES    TYPE
driver_hourly_stats          {'driver'}  FeatureView
driver_hourly_stats_fresh    {'driver'}  FeatureView
transformed_conv_rate        {'driver'}  OnDemandFeatureView
transformed_conv_rate_fresh  {'driver'}  OnDemandFeatureView
```

`feast entities list`
```
(feast) ➜  feature_repo git:(mariadb) ✗ feast entities list;
zsh: /usr/local/bin/feast: bad interpreter: /usr/local/opt/python@3.11/bin/python3.11: no such file or directory
NAME    DESCRIPTION    TYPE
driver                 ValueType.UNKNOWN
```

## These steps are to deploy feast on openshift 

- **Add Permissions to Security Context Constraint (SCC)**:
      
     ```
     oc adm policy add-scc-to-user anyuid -z default -n <namespace>>
     ``` 
- Add the Feast Helm repository and update:
     ```
      helm repo add feast-charts https://feast-helm-charts.storage.googleapis.com
      helm repo update
     ```

- Deploy Feast on Openshift using Helm, by setting `feature_store.yaml` file as a base64 string from feature_repo directory:
      ```
      helm install feast-release feast-charts/feast-feature-server --set feature_store_yaml_base64=$(base64 < feature_store.yaml) 
      ```
  
`feature_store.yaml` file -- 
```
project: feast_postgres
provider: aws
registry:
    registry_type: sql
    path: mysql://feast:feast@mariadb.feast-example.svc.cluster.local:3306/sampledb
    cache_ttl_seconds: 60
online_store:
    type: postgres
    host: postgresql.feast-example.svc.cluster.local
    port: 5432
    database: sampledb
    db_schema: feast
    user: feast
    password: feast
offline_store:
    type: postgres
    host: postgresql.feast-example.svc.cluster.local
    port: 5432
    database: sampledb
    db_schema: feast
    user: feast
    password: feast
entity_key_serialization_version: 2
``` 

### Step 5: Validating the local feast deployment -
Do `feast apply` -- 
If it complains about tables not present in the offline store --> Navigate to openshift and login into postgres and create a table --
 ```
 sh-4.4$ psql -U feast -W
Password for user feast: 
psql (10.23)
Type "help" for help.

feast=> \l
                                 List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges   
-----------+----------+----------+------------+------------+-----------------------
 feast     | feast    | UTF8     | en_US.utf8 | en_US.utf8 | 
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 | 
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
           |          |          |            |            | postgres=CTc/postgres
(4 rows)

feast-> \dt
            List of relations
 Schema |      Name      | Type  | Owner 
--------+----------------+-------+-------
 feast  | feast_registry | table | feast
 public | feast_table    | table | feast
(2 rows)

feast=> CREATE TABLE feast_driver_hourly_stats (
    driver_id INT,
    event_timestamp TIMESTAMP,
    created TIMESTAMP,
    conv_rate FLOAT,
    acc_rate FLOAT,
    avg_daily_trips INT
);
CREATE TABLE
feast=> \dt
                 List of relations
 Schema |           Name            | Type  | Owner 
--------+---------------------------+-------+-------
 feast  | feast_driver_hourly_stats | table | feast
 feast  | feast_registry            | table | feast
 public | feast_table               | table | feast
(3 rows)
```

then do `feast apply` for the tables to populate -- 

```
feast=> \dt
                        List of relations
 Schema |                  Name                   | Type  | Owner 
--------+-----------------------------------------+-------+-------
 feast  | feast_driver_hourly_stats               | table | feast
 feast  | feast_mariadb_driver_hourly_stats       | table | feast
 feast  | feast_mariadb_driver_hourly_stats_fresh | table | feast
 feast  | feast_registry                          | table | feast
 public | feast_table                             | table | feast
(5 rows)

feast=> SELECT * FROM feast_mariadb_driver_hourly_stats;
 entity_key | feature_name | value | event_ts | created_ts 
------------+--------------+-------+----------+------------
(0 rows)

feast=> SELECT * FROM feast_mariadb_driver_hourly_stats_fresh;
 entity_key | feature_name | value | event_ts | created_ts 
------------+--------------+-------+----------+------------
(0 rows)

 ```

5. Now navigate to openshift and validate --> mariabdb pod -- 
```
sh-4.4$ mysql -u  feast -p
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 15966
Server version: 10.3.39-MariaDB MariaDB Server

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]> USE feast;
Database changed
MariaDB [feast]> SHOW TABLES;
+-------------------------+
| Tables_in_feast         |
+-------------------------+
| data_sources            |
| entities                |
| feast_metadata          |
| feature_services        |
| feature_views           |
| managed_infra           |
| on_demand_feature_views |
| request_feature_views   |
| saved_datasets          |
| stream_feature_views    |
| validation_references   |
+-------------------------+
11 rows in set (0.000 sec)
```

```
MariaDB [feast]> SELECT * FROM entities;
+-------------+---------------+------------------------+-----------------------------------------------------+
| entity_name | project_id    | last_updated_timestamp | entity_proto                                        |
+-------------+---------------+------------------------+-----------------------------------------------------+
| driver      | feast_mariadb |             1711133550 | 
```
```
MariaDB [feast]> SELECT * FROM feature_views;
| feature_view_name         | project_id    | last_updated_timestamp | materialized_intervals | feature_view_proto
| driver_hourly_stats       | feast_mariadb |             1711133901 | NULL                   | 

driver_hourly_statsdriver"
        conv_rate"

acc_rate"
avg_daily_trips*

| driver_hourly_stats_fresh | feast_mariadb |             1711133902 | NULL                   | 
Ò
driver_hourly_stats_freshdriver"
        conv_rate"

acc_rate"
avg_daily_trips*
teamdriver_performance£event_timestamp*createdi
```

On your Local you can materialize feast as below -- 

`feast feature-views list`

```
NAME                         ENTITIES    TYPE
driver_hourly_stats          {'driver'}  FeatureView
driver_hourly_stats_fresh    {'driver'}  FeatureView
transformed_conv_rate        {'driver'}  OnDemandFeatureView
transformed_conv_rate_fresh  {'driver'}  OnDemandFeatureView
```
![driver.png](driver.png)

```
(base) ➜  feature_repo git:(mariadb) ✗ feast materialize-incremental "2024-03-22T10:00:00"
```
![output.png](output.png)

## Conclusion
In conclusion, this exercise showcases the integration of MariaDB with Feast for a scalable registry solution, alongside PostgreSQL for both online and offline feature stores. By leveraging MariaDB's robustness for the registry and PostgreSQL's versatility for feature storage, this setup offers a comprehensive and efficient infrastructure for managing machine learning features. This approach not only enhances the scalability and reliability of the feature store but also optimizes the performance of machine learning workflows, making it an ideal choice for teams aiming to deploy machine learning models with high efficiency and accuracy.
