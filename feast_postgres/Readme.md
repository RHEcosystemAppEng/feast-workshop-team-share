###  1. Install PostgreSQL on Openshift using OpenShift Template



![postgres.png](postgres.png)


![postgres-1.png](postgres-1.png)

### 2. Create a feature repository


![create-feast-postgres.png](create-feast-postgres.png)

### 3. Port Forward PostgreSQL Database 

```
oc port-forward   postgresql-1-fgn46 5432
```

### 4. Create Feature Store Deployment

```
cd feature_repo 
feast apply
```

- **Verify that the Postgres DB is updated with the Feast Registry**.

![postgres-feast-registry.png](postgres-feast-registry.png)


### 5. Deploy Feature Server Instances on Openshift:

Set the environment variables in [feature_store.yaml](feature_repo%2Ffeature_store.yaml) and its will be to look like as

  ```yaml
          project: feast_postgres
          provider: local
          registry:
               registry_type: sql
               path: postgresql://${PG_USERNAME}:${PG_PASSWORD}@127.0.0.1:5432/feast
               cache_ttl_seconds: 60
               sqlalchemy_config_kwargs:
                    echo: true
                    pool_pre_ping: true
          online_store:
              type: postgres
              host: postgresql.feast.svc.cluster.local
              port: 5432
              database: feast
              db_schema: feast
              user: ${PG_USERNAME}
              password: ${PG_PASSWORD}
          offline_store:
              type: postgres
              host: postgresql.feast.svc.cluster.local
              port: 5432
              database: feast
              db_schema: feast
              user: ${PG_USERNAME}
              password: ${PG_PASSWORD}
          entity_key_serialization_version: 2
 ```

   - **Add Permissions to Security Context Constraint (SCC)**:
      
     ```bash
     oc adm policy add-scc-to-user anyuid -z default -n <namespace>>
     ``` 
   - Add the Feast Helm repository and update:
       ```bash
          helm repo add feast-charts https://feast-helm-charts.storage.googleapis.com
          helm repo update
       ```

   - Deploy Feast on Openshift using Helm, by setting `feature_store.yaml` file as a base64 string from feature_repo directory:
      ```bash
             helm install feast-release feast-charts/feast-feature-server \
             --set feature_store_yaml_base64=$(base64 < feature_store.yaml) 
      ```
### 6. Testing and Verification
![feast-test.png](feast-test.png)