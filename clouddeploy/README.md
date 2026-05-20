# Copy the images to sandbox 
   ```
    docker pull europe-west2-docker.pkg.dev/ons-ci-rmrasbs/images/response-operations-ui:3.1.167
    docker tag europe-west2-docker.pkg.dev/ons-ci-rmrasbs/images/response-operations-ui:3.1.167 europe-west2-docker.pkg.dev/ras-rm-sandbox/images/response-operations-ui:3.1.167
    docker push europe-west2-docker.pkg.dev/ras-rm-sandbox/images/response-operations-ui:3.1.167
   ```

# Create release

```
gcloud deploy releases create mresponse-operations-ui-001 --source=. \
--project=ras-rm-sandbox \
--region=europe-west2 \
--delivery-pipeline=response-operations-ui
```
