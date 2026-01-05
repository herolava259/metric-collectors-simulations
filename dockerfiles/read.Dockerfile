FROM alpine
WORKDIR /content_check 

COPY . . 
RUN ls -R 
