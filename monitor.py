#!/usr/bin/env python3

# Import the SDKs
import datadog
import docker
import time

# Credentials
docker_hub_username = ""
docker_hub_password = ""

datadog_api_key = ""
datadog_app_key = ""

docker_repo = "locnh/busybox"

# Main
is_healthy = True

# Check
try:
    client = docker.from_env()
    client.login(username=docker_hub_username, password=docker_hub_password)

    # Clean up
    try:
        print("Cleaning the floor ..")
        for container in client.containers.list(all):
            container.remove(force=True)

        for image in client.images.list():
            client.images.remove(image.id)
    except:
        pass

    print("Pulling image ...")
    client.images.pull("busybox", tag="latest")

    print("Starting container ...")
    container = client.containers.run("busybox", "date > /check.log", detach=True)

    print("Making change and commit to image ...")
    container.commit(docker_repo, tag="test")

    print("Pushing image ...")
    running_time = time.time()
    client.images.push("%s:test" % docker_repo)
    running_time = time.time() - running_time
except:
    is_healthy = False

if is_healthy:
    print("I'm good")
    print("Pushing in %s seconds" % running_time)
else:
    print("Having cancer")

# Datadog sending
options = {
    'api_key': datadog_api_key,
    'app_key': datadog_app_key
}

print("Sending metrics to datadog ...")
datadog.initialize(**options)
datadog.api.Metric.send(metric='registry.healthcheck.runningtime', points=(time.time(), running_time))
datadog.api.Metric.send(metric='registry.healthcheck.is_healthy', points=(time.time(), is_healthy))
