# metric-collectors-simulations


## Requirements
- Following by microservices 
- Include:
    + demo services (>= 2 services)
    + Sending Alert when incidents occur.
### Contexts
- The company's building monitoring system, collect cpu usages, ram usage, disk space...
- Each services will send periodically the infromation to the monitoring system

### Architechtures

![Artchitechture](assets/Screenshot%202025-12-29%20092342.png)

### Technologies
- Fast-API
- RabbitMQ
- SQL-Lite (for demo)
- PostgresQL
- Telegram
- nginx