# Vector Database for Python Developers
`any-vector-db` is a simple, user-friendly solution for Python developers looking to create their own vector database with CRUD support. Vector databases are a key component of the stack needed to use LLMs as they allow them to have access to context and memory. Many of the solutions out there require developers and users to use complex solutions that are often not needed. With `any-vector-db`, you can easily create your own vector database solution that can work locally and can still be easily deployed and served with scalability features such as sharding and replication. 

`any-vector-db` allows you to start simple and work locally while allowing when needed to deploy and scale in a seamless manner. With the help of [DocArray](https://github.com/docarray/docarray) and [Jina](https://github.com/jina-ai/jina) `any-vector-db` allows developers to focus on the algorithmic part and tweak the core of the vector search with Python as they want while keeping it easy to scale and deploy the solution. 

## :muscle: Features

- User-friendly interface: Vector Database is designed with simplicity and ease of use in mind, making it accessible even for beginners.

- CRUD support: Just provide Python implementations for interfaces implementing CRUD interactions or use any of the provided implementations.  

- Customizable: Vector Database can be easily adapted to suit your specific needs, so you can build the database you want and for any input and output schema you want with the help of [DocArray](https://github.com/docarray/docarray).

- Serve: Serve the databases to insert or search as a service with `gRPC` or `HTTP` protocol.

- Scalable: With Vector Database, you can deploy your database in the cloud and take advantage of powerful scalability features like sharding and replication. With this, you can easily improve the latency of your service by sharding your data, or improve the availability and throughput by allowing `any-vector-db` to offer replication.

- Serve in the cloud: If you need to deploy your service in the cloud, you can easily deploy in [Jina AI Cloud](). More deployment options will soon come. 

- Serverless capacity: Databases can be deployed in the cloud in serverless mode, allowing you to save resources and have the data available only when needed. # TODO: Clarify

## Getting Started with prebuilt databases

To get started with Vector Database, simply follow these easy steps:

- Install `any-vector-db`: 

```pip install any-vector-db```

- Use any of the pre-built databases as a Python class: 

```python
from any_vector_db import HNSWLibTextDatabase
from docarray import DocList
from docarray.documents import TextDoc

db = HNSWLibTextDatabased(data_path='./hnwslib_path')

db.index(inputs=DocList[TextDoc]([TextDoc(text=f'index {i}', embedding=np.random.rand(128))for i in range(1000)]))

results = db.search(inputs=DocList[TextDoc]([TextDoc(text='query', embedding=np.random.rand(128)]), parameters={'limit': 10})
```

- Serve the database as a service

```python

from any_vector_db import HNSWLibTextDatabase
from docarray import DocList
from docarray.documents import TextDoc

db = HNSWLibTextDatabased(data_path='./hnwslib_path')

with db.serve(port=12345) as service:
   service.block()
```

- Interact with the database through a client on a similar way as previously:

```python
from any_vector_db import Client

c = Client(port=12345)

c.index()
c.search()
```


## Customize your Database

TODO: Explain how to write your own implementation

## Scale your own Database, add replication and sharding

TODO: Explain how and why you would add replicas and shards

## Deploy it to the cloud

TODO: Explain how and why you would deploy to JCloud.


## Roadmap
We have big plans for the future of Vector Database! Here are some of the features we have in the works:

Serverless capacity: We're working on adding serverless capacity to Vector Database, making it even easier to deploy in the cloud.
More pre-built databases: We want to give you even more pre-built solutions for your database.
More deploying options: We want to enable deploying Vector Databases on different cloud with more options
Support

If you need any help with `any-vector-db`, or you are interested on using it and have some requests to make it fit your own need. don't hesitate to reach out to us. You can join our [Slack community](https://jina.ai/slack) and chat with us and other community members.

Contributing
We welcome contributions from the community! If you have an idea for a new feature or improvement, please let us know. We're always looking for ways to make `any-vector-db` better for our users.

