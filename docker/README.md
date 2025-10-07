# Docker image for DC3

---
## Build

Start the build

- Set the tag (do not use `latest` or `stable`)
```bash
export IMAGE_TAG=0.1.0
```
- Build the image
```bash
docker build \
  --progress=plain \
  --no-cache \
  -f docker/Dockerfile \
  -t ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:$IMAGE_TAG \
  .
```

---
## Test the image

- Start a container:
    - In console mode
```bash
docker run -it --rm --name dc3 ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:$IMAGE_TAG
```
    - In graphical mode (jupyterlab)
```bash
docker run -it --rm -p 8888:8888 --name dc3-lab ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:$IMAGE_TAG
```
- Run an evaluation
```bash
cd ~/work
mkdir tests
python ./dc3/evaluate.py \
   --logfile ./tests/dc3.log \
   --data_directory ./tests/data
```
- Remove the container
    - In console mode
```bash
docker rm --force dc3
```
    - In graphical mode (jupyterlab)
```bash
docker rm --force dc3-lab
```

---
## Publish the image to the Github registry

```bash
docker push ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:$IMAGE_TAG
```

---
## Set the `latest` and `stable` versions

- stable
```bash
# Define TAG used for stable
export TAG_FOR_STABLE=0.1.0

# Pull image
docker pull ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:$TAG_FOR_STABLE
# Tag it as stable
docker tag ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:$TAG_FOR_STABLE ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:stable
# And push it
docker push ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:stable
```
- latest
```bash
# Define TAG used for latest 
export TAG_FOR_LATEST=0.1.0

# Pull image
docker pull ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:$TAG_FOR_LATEST
# Tag it as latest
docker tag ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:$TAG_FOR_LATEST ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:latest
# And push it
docker push ghcr.io/ocean-ai-data-challenges/dc-sea-ice-forecasting:latest
```
