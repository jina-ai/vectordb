# Vector Database for Python Developers
`any-vector-db` is a simple, user-friendly solution for Python developers looking to create their own vector database with CRUD support. Vector databases are a key component of the stack needed to use LLMs as they allow them to have access to context and memory. Many of the solutions out there require developers and users to use complex solutions that are often not needed. With `any-vector-db`, you can easily create your own vector database solution that can work locally and still be easily deployed and served with scalability features such as sharding and replication. 

`any-vector-db` allows you to start simple and work locally while allowing when needed to deploy and scale in a seamless manner. With the help of [DocArray](https://github.com/docarray/docarray) and [Jina](https://github.com/jina-ai/jina) `any-vector-db` allows developers to focus on the algorithmic part and tweak the core of the vector search with Python as they want while keeping it easy to scale and deploy the solution.

Stop wondering what exact algorithms do existing solutions apply, how do they apply filtering or how to map your schema to their solutions, with `any-vector-db` you as a Python developer can easily understand and control what is the vector search algorithm doing, giving you the full control if needed while supporting you for local setting and in more advanced and demanding scenarios in the cloud.

## :muscle: Features

- User-friendly interface: `any-vector-db` is designed with simplicity and ease of use in mind, making it accessible even for beginners.

- Adapts to your needs: `any-vector-db` is designed to offer what you need without extra complexity, supporting the features needed at every step. From local, to serve, to the cloud in a seamless way.

- CRUD support: `any-vector-db` support CRUD operations, index, search, update and delete.

- Serve: Serve the databases to insert or search as a service with `gRPC` or `HTTP` protocol.

- Scalable: With `any-vector-db`, you can deploy your database in the cloud and take advantage of powerful scalability features like sharding and replication. With this, you can easily improve the latency of your service by sharding your data, or improve the availability and throughput by allowing `any-vector-db` to offer replication.

- Deploy to the cloud: If you need to deploy your service in the cloud, you can easily deploy in [Jina AI Cloud](). More deployment options will soon come. 

- Serverless capacity: `any-vector-db` can be deployed in the cloud in serverless mode, allowing you to save resources and have the data available only when needed.

- Multiple ANN algorithms: `any-vector-db` contains different implementations of ANN algorithms. These are the ones offered so far, we plan to integrate more:
   - Exact NN Search: Implements Simple Nearest Neighbour Algorithm.   
   - HNSWLib: Based on [HNSWLib](https://github.com/nmslib/hnswlib)

- Filter capacity: `any-vector-db` allows you to have filters on top of the ANN search.

- Customizable: `any-vector-db` can be easily extended to suit your specific needs or schemas, so you can build the database you want and for any input and output schema you want with the help of [DocArray](https://github.com/docarray/docarray).

## 🏁 Getting Started

To get started with Vector Database, simply follow these easy steps, in this example we are going to use `HNSWVecDB` as example:

1. Install `any-vector-db`: 

```pip install any-vector-db```

2. Define your Index Document schema or use any of the predefined ones using [DocArray](https://docs.docarray.org/user_guide/representing/first_step/):

```python
from docarray import BaseDoc
from docarray.text import TextDoc

class MyTextDoc(TextDoc):
   author: str = ''
```

3. Use any of the pre-built databases with the document schema as a Python class: 

```python
from any_vector_db import HNSWLibDB
db = HNSWLibDB[MyTextDoc](data_path='./hnwslib_path')

db.index(inputs=DocList[MyTextDoc]([MyTextDoc(text=f'index {i}', embedding=np.random.rand(128)) for i in range(1000)]))
results = db.search(inputs=DocList[MyTextDoc]([MyTextDoc(text='query', embedding=np.random.rand(128)]), parameters={'limit': 10})
```

Each result will contain the matches under the `.matches` attribute as a `DocList[MyTextDoc]`

4. Serve the database as a service

```python
with HNSWLibDB[MyTextDoc].serve(config={'data_path'= './hnswlib_path'}, port=12345, replicas=1, shards=1) as service:
   service.block()
```

5. Interact with the database through a client in a similar way as previously:

```python
from any_vector_db import Client

c = Client[MyTextDoc](port=12345)

c.index(inputs=DocList[TextDoc]([TextDoc(text=f'index {i}', embedding=np.random.rand(128)) for i in range(1000)]))
results = c.search(inputs=DocList[TextDoc]([TextDoc(text='query', embedding=np.random.rand(128)]), parameters={'limit': 10})
```

## :cloud: Deploy it to the cloud

`any-vector-db` allows you to deploy your solution to the cloud easily. 

1. First, you need to get a [Jina AI Cloud](https://cloud.jina.ai/) account

2. Login to your Jina AI Cloud account using the `jc` command line:

```jc login```

3. Deploy:
```python
HNSWLibDB[MyTextDoc].deploy(config={'data_path'= './hnswlib_path'}, replicas=1, shards=1)
```

You can then list and delete your deployed DBs with `jc`:

```jc list <>```

```jc delete <>```


## :rocket: Scale your own Database, add replication and sharding

When serving or deploying your Vector Databases you can set 2 scaling parameters and `any-vector-db`:

- Shards: The number of shards in which the data will be split. This will allow for better latency. `any-vector-db` will make sure that Documents are indexed in only one of the shards, while search request will be sent to all the shards and `any-vector-db` will make sure to merge the results from all shards.

- Replicas: The number of replicas of the same DB that must exist. The given replication factor will be shared by all the `shards`. `any-vector-db` uses RAFT algorithm to ensure that the index is in sync between all the replicas of each shard. With this, `any-vector-db` increases the availability of the service and allows for better search throughput as multiple replicas can respond in parallel to more search requests while allowing CRUD operations. 

** When deployed, the number of replicas will be set to 1. We are working to enable replication in the cloud

## 🛠️ (Optional) Customize your Database

TODO: Explain how to write your own implementation


## 🛣️ Roadmap

We have big plans for the future of Vector Database! Here are some of the features we have in the works:

- Serverless capacity: We're working on adding serverless capacity to `any-vector-db` in the cloud. We currenly allow to scale between 0 and 1 replica, we aim to offer from 0 to N.
- More ANN search algorithms: We want to support more ANN search algorithms

- More deploying options: We want to enable deploying `any-vector-db` on different clouds with more options

If you need any help with `any-vector-db`, or you are interested on using it and have some requests to make it fit your own need. don't hesitate to reach out to us. You can join our [Slack community](https://jina.ai/slack) and chat with us and other community members.

## Contributing

We welcome contributions from the community! If you have an idea for a new feature or improvement, please let us know. We're always looking for ways to make `any-vector-db` better for our users.

