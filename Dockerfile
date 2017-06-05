FROM python:2.7

# create source directory
RUN mkdir /root/woosh-server
ADD start.py requirements.txt /root/woosh-server/
ADD server /root/woosh-server/server
ADD resources /root/woosh-server/resources

# add dependencies
RUN pip install -r /root/woosh-server/requirements.txt
RUN mkdir /root/woosh-server/www

# configure runtime
EXPOSE 3000
ENTRYPOINT cd /root/woosh-server && \
           python /root/woosh-server/start.py
