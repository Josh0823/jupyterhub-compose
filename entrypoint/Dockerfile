FROM jupyterhub/jupyterhub

# RUN \
#     apt-get update          &&  \
#     apt-get upgrade --yes   &&  \
#     apt-get install --yes       \
#         git

# RUN \
#     pip3 install git+https://github.com/Josh0823/entrypoint-service.git

RUN pip3 install --no-cache-dir aiocache

# WORKDIR /srv
ADD docker-entrypoint.sh docker-entrypoint.sh
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python3", "-u", "-m", "entrypoint_dev/jupyterhub_entrypoint"]
