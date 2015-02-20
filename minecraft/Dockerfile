FROM ubuntu:14.04

MAINTAINER Kord Campbell <kordless@stackgeek.com>
RUN echo "foo"

# aptitude updates
RUN apt-get update -y
RUN apt-get install -y python3-software-properties
COPY add-apt-repository.py ./add-apt-repository
RUN chmod 755 add-apt-repository
RUN mv add-apt-repository /usr/bin/

# java install
RUN add-apt-repository -y ppa:webupd8team/java
RUN apt-get update
RUN echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
RUN echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
RUN apt-get -y install oracle-java7-installer

# craftbucket mod
RUN mkdir /opt/minecraft/
RUN wget -q http://stackgeek.s3.amazonaws.com/minecraft.jar -O /opt/minecraft/minecraft.jar

# install scriptcraft
RUN mkdir /opt/minecraft/plugins/
RUN wget -q http://scriptcraftjs.org/download/2014-08/20140823/scriptcraft.jar -O /opt/minecraft/plugins/scriptcraft.jar

# agree to the EULA
RUN echo "eula=true" > /opt/minecraft/eula.txt
RUN cp /opt/minecraft/eula.txt ./eula.txt

# clean up
RUN apt-get clean && \
	rm -rf /var/lib/apt/lists/*

CMD ["java", "-Xms256m", "-Xmx256m", "-jar", "/opt/minecraft/minecraft.jar", "nogui"]

EXPOSE 25565
