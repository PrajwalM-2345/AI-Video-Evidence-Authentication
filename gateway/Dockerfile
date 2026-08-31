FROM maven:3.9-eclipse-temurin-21

WORKDIR /app

# Copy the pom.xml and download dependencies using global 'mvn'
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the rest of the source code
COPY src ./src

# Use global 'mvn' command
CMD ["mvn", "spring-boot:run"]