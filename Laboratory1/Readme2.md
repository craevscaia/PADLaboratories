# Welcome to my project

See the Postaman collection bellow
https://documenter.getpostman.com/view/23334469/2s9YRE1Wek

Just press run in browser and magic happens

### Run it

https://hub.docker.com/repository/docker/craevscaia/pad

Copy the images from the docker repository.
Run them
Instances:

4 instances of microservices

2 databases

1 api-gateway

1 service-discovery

# Online BookStore

### Trip Circuit Breaker if multiple reroutes happen

The Circuit Breaker pattern is a design pattern used in software development to detect failures and
encapsulate the logic of preventing a failure from constantly recurring during maintenance,
temporary external system failure, or unexpected system difficulties.

Circuit Breaker pattern detect these failures and "trip" the circuit breaker,
which prevents further communication with that service until it has had a chance to recover.

By "multiple re-routes" is meant that the service is trying to connect to another service,
and that service is not responding properly, it could adapt the code to throw an exception when a reroute is detected.

The circuit breaker would then count these exceptions, and if they reach the threshold,
it would trip the circuit, preventing further reroutes and giving the system time to recover.

### Service High Availability

1. Ensure services are stateless and can be scaled horizontally.
2. Use a load balancer to distribute traffic.
3. Deploy services in a containerized environment like Kubernetes for easy scaling and management.
4. Health Checks - implement monitoring tools to keep track of the application’s health and performance.
5. Set up alerts to notify when something goes wrong, or the response time goes above a certain threshold.

### ELK stack or Prometheus + Grafana for logging. Aggregate data from all services

Logging and monitoring are essential for maintaining the health, performance, and reliability of the applications.

1. **ELK Stack:** This stands for Elasticsearch, Logstash, and Kibana. Need to configure
   Logstash to collect logs from your services, store them in Elasticsearch, and use Kibana to visualize
   the logs.

**Install Elasticsearch:** This is a search and analytics engine.

**Install Logstash:** This is a server-side data processing pipeline that ingests data from multiple sources
simultaneously, transforms it, and then sends it to Elasticsearch.

**Install Kibana:** This is a visualization layer that works on top of Elasticsearch.

2. **Prometheus + Grafana:** Prometheus can be used for monitoring and alerting, while Grafana can
   be used for visualization. Configure your services to expose metrics in a format that Prometheus can
   scrape.

### Implement microservice-based 2 Phase Commits for a endpoint that create changes more than in one database

Two-phase commit (2PC) is a type of atomic commitment protocol (ACP).
It is a distributed algorithm that lets all participants of a distributed transaction decide
together whether to commit or abort (rollback) the transaction.
The protocol achieves its goal even when some of the participants or
the coordinator fail during the protocol.

This is complex and typically avoided, but if necessary:

1. Implement a transaction coordinator service.
2. Ensure all participating services can prepare, commit, and rollback transactions.

### Consistent Hashing for Cache

Consistent hashing is a distribution scheme that provides hash table functionality in
a way that the addition or removal of one slot does not significantly change
the mapping of keys to slots.

1. Use a distributed cache like Redis.
2. Implement consistent hashing to ensure even distribution of cache keys.

### Cache High Availability

Achieving high availability in caching involves ensuring that the cache is available and responsive
at all times, even in the event of failures.
This usually means having redundancy, replication,
and potentially a load balancer to distribute the requests.

1. Set up a Redis Cluster for distributed caching with high availability.

### 2 Phase Commits Long-Running Saga Transactions with Coordinator

### Database redundancy/replication + failover (one database, min 4 repl.)

### Create a Data Warehouse that will be periodically updated with all data from the databases.