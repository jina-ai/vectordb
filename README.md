<p align="center">
<a href="https://docs.jina.ai"><img src="https://github.com/jina-ai/vectordb/blob/main/.github%2Fimages%2Fvectordb-logo.png?raw=true" alt="VectorDB from Jina AI logo" width="300px"></a>
</p>

<p align="center">
<b>A Python vector database you just need - no more, no less.</b>
</p>

<p align=center>
<a href="https://pypi.org/project/vectordb/"><img alt="PyPI" src="https://img.shields.io/pypi/v/vectordb?label=Release&style=flat-square"></a>
<a href="https://discord.jina.ai"><img src="https://img.shields.io/discord/1106542220112302130?logo=discord&logoColor=white&style=flat-square"></a>
<a href="https://pypistats.org/packages/vectordb"><img alt="PyPI - Downloads from official pypistats" src="https://img.shields.io/pypi/dm/vectordb?style=flat-square"></a>
<a href="https://github.com/jina-ai/vectordb/actions/workflows/cd.yml"><img alt="Github CD status" src="https://github.com/jina-ai/vectordb/actions/workflows/cd.yml/badge.svg"></a>
</p>

`vectordb` is a Pythonic vector database offers a comprehensive suite of [CRUD](#crud-support) (Create, Read, Update, Delete) operations and robust [scalability options, including sharding and replication](#scaling-your-db). It's readily deployable in a variety of environments, from [local](#getting-started-with-vectordb-locally) to [on-premise](#getting-started-with-vectordb-as-a-service) and [cloud](#hosting-vectordb-on-jina-ai-cloud). `vectordb` delivers exactly what you need - no more, no less. It's a testament to effective Pythonic design without over-engineering, making it a lean yet powerful solution for all your needs.



`vectordb` capitalizes on the powerful retrieval prowess of [DocArray](https://github.com/docarray/docarray) and the scalability, reliability, and serving capabilities of [Jina](https://github.com/jina-ai/jina). Here's the magic: DocArray serves as the engine driving vector search logic, while Jina guarantees efficient and scalable index serving. This synergy culminates in a robust, yet user-friendly vector database experience - that's `vectordb` for you.



<!--In simple terms, one can think as [DocArray](https://github.com/docarray/docarray) being a the `Lucene` algorithmic logic for Vector Search powering the retrieval capabilities and [Jina](https://github.com/jina-ai/jina), the ElasticSearch making sure that the indexes are served and scaled for the clients, `vectordb` wraps these technologies to give a powerful and easy to use experience to
use and develop vector databases.-->

<!--(THIS CAN BE SHOWN WHEN CUSTOMIZATION IS ENABLED) `vectordb` allows you to start simple and work locally while allowing when needed to deploy and scale in a seamless manner. With the help of [DocArray](https://github.com/docarray/docarray) and [Jina](https://github.com/jina-ai/jina) `vectordb` allows developers to focus on the algorithmic part and tweak the core of the vector search with Python as they want while keeping it easy to scale and deploy the solution. -->

<!--(THIS CAN BE SHOWN WHEN CUSTOMIZATION IS ENABLED) Stop wondering what exact algorithms do existing solutions apply, how do they apply filtering or how to map your schema to their solutions, with `vectordb` you as a Python developer can easily understand and control what is the vector search algorithm doing, giving you the full control if needed while supporting you for local setting and in more advanced and demanding scenarios in the cloud. -->  

## Install

```bash
pip install vectordb
```

<table>
  <tr>
    <td>
      <a href="#getting-started-with-vectordb-locally">
        <img src="https://github.com/jina-ai/vectordb/blob/main/.github%2Fimages%2Fguide-1.png?raw=true" alt="Use vectordb from Jina AI locally" width="100%">
      </a>
    </td>
    <td>
      <a href="#getting-started-with-vectordb-as-a-service">
        <img src="https://github.com/jina-ai/vectordb/blob/main/.github%2Fimages%2Fguide-2.png?raw=true" alt="Use vectordb from Jina AI as a service" width="100%">
      </a>
    </td>
    <td>
      <a href="#hosting-vectordb-on-jina-ai-cloud">
        <img src="https://github.com/jina-ai/vectordb/blob/main/.github%2Fimages%2Fguide-3.png?raw=true" alt="Use vectordb from Jina AI on Jina AI Cloud" width="100%">
      </a>
    </td>
  </tr>
</table>



## Getting started with `vectordb` locally

1. Kick things off by defining a Document schema with the [DocArray](https://docs.docarray.org/user_guide/representing/first_step/) dataclass syntax:

```python
from docarray import BaseDoc
from docarray.typing import NdArray

class ToyDoc(BaseDoc):
  text: str = ''
  embedding: NdArray[128]
```

2. Opt for a pre-built database (like `InMemoryExactNNVectorDB` or `HNSWVectorDB`), and apply the schema:

```python
from docarray import DocList
import numpy as np
from vectordb import InMemoryExactNNVectorDB, HNSWVectorDB

# Specify your workspace path
db = InMemoryExactNNVectorDB[ToyDoc](workspace='./workspace_path')

# Index a list of documents with random embeddings
doc_list = [ToyDoc(text=f'toy doc {i}', embedding=np.random.rand(128)) for i in range(1000)]
db.index(inputs=DocList[ToyDoc](doc_list))

# Perform a search query
query = ToyDoc(text='query', embedding=np.random.rand(128))
results = db.search(inputs=DocList[ToyDoc]([query]), limit=10)

# Print out the matches
for m in results[0].matches:
  print(m)
```

Since we issued a single query, `results` contains only one element. The nearest neighbour search results are conveniently stored in the `.matches` attribute.

## Getting started with `vectordb` as a service

`vectordb` is designed to be easily served as a service, supporting `gRPC`, `HTTP`, and `Websocket` communication protocols. 

### Server Side

On the server side, you would start the service as follows:

```python
with db.serve(protocol='grpc', port=12345, replicas=1, shards=1) as service:
   service.block()
```

This command starts `vectordb` as a service on port `12345`, using the `gRPC` protocol with `1` replica and `1` shard.

### Client Side
On the client side, you can access the service with the following commands:

```python
from vectordb import Client

# Instantiate a client connected to the server. In practice, replace 0.0.0.0 to the server IP address.
client = Client[ToyDoc](address='grpc://0.0.0.0:12345')

# Perform a search query
results = client.search(inputs=DocList[ToyDoc]([query]), limit=10)
```

This allows you to perform a search query, receiving the results directly from the remote `vectordb` service.


## Hosting `vectordb` on Jina AI Cloud

You can seamlessly deploy your `vectordb` instance to Jina AI Cloud, which ensures access to your database from any location.

Start by embedding your database instance or class into a Python file:

```python
# example.py
from docarray import BaseDoc
from vectordb import InMemoryExactNNVectorDB

db = InMemoryExactNNVectorDB[ToyDoc](workspace='./vectordb') # notice how `db` is the instance that we want to serve

if __name__ == '__main__':
    # IMPORTANT: make sure to protect this part of the code using __main__ guard
    with db.serve() as service:
        service.block()
```

Next, follow these steps to deploy your instance:

1. If you haven't already, sign up for a [Jina AI Cloud](https://cloud.jina.ai/) account.

2. Use the `jc` command line to login to your Jina AI Cloud account:

```bash
jc login
```

3. Deploy your instance:

```bash
vectordb deploy --db example:db
```

![](./.github/images/vectordb_deploy_screenshot.png)

### Connect from the client

After deployment, use the `vectordb` Client to access the assigned endpoint:

```python
from vectordb import Client

# replace the ID with the ID of your deployed DB as shown in the screenshot above
c = Client(address='grpcs://ID.wolf.jina.ai')
```

### Manage your deployed instances using [jcloud](https://github.com/jina-ai/jcloud)

You can then list, pause, resume or delete your deployed DBs with `jc` command:

```jcloud list ID```

![](./.github/images/vectordb_deploy_list.png)

```jcloud pause ID``` or ```jcloud resume ID```

![](./.github/images/vectordb_deploy_paused.png)

```jcloud remove ID```
   

## Advanced Topics

### What is a vector database?

Vector databases serve as sophisticated repositories for embeddings, capturing the essence of semantic similarity among disparate objects. These databases facilitate similarity searches across a myriad of multimodal data types, paving the way for a new era of information retrieval. By providing contextual understanding and enriching generation results, vector databases greatly enhance the performance and utility of Language Learning Models (LLM). This underscores their pivotal role in the evolution of data science and machine learning applications.

### CRUD support

Both the local library usage and the client-server interactions in `vectordb` share the same API. This provides `index`, `search`, `update`, and `delete` functionalities:

- `index`: Accepts a `DocList` to index.
- `search`: Takes a `DocList` of batched queries or a single `BaseDoc` as a single query. It returns either single or multiple results, each with `matches` and `scores` attributes sorted by `relevance`.
- `delete`: Accepts a `DocList` of documents to remove from the index. Only the `id` attribute is necessary, so make sure to track the `indexed` `IDs` if you need to delete documents.
- `update`: Accepts a `DocList` of documents to update in the index. The `update` operation will replace the `indexed` document with the same index with the attributes and payload from the input documents.

### Service endpoint configuration

You can serve `vectordb` and access it from a client with the following parameters:

- protocol: The serving protocol. It can be `gRPC`, `HTTP`, `websocket` or a combination of them, provided as a list. Default is `gRPC`.
- port: The service access port. Can be a list of ports for each provided protocol. Default is 8081.
- workspace: The path where the VectorDB persists required data. Default is '.' (current directory).

### Scaling your DB

You can set two scaling parameters when serving or deploying your Vector Databases with `vectordb`:

- Shards: The number of data shards. This improves latency, as `vectordb` ensures Documents are indexed in only one of the shards. Search requests are sent to all shards and results are merged.
- Replicas: The number of DB replicas. `vectordb` uses the [RAFT](https://raft.github.io/) algorithm to sync the index between replicas of each shard. This increases service availability and search throughput, as multiple replicas can respond in parallel to more search requests while allowing CRUD operations. Note: In JCloud deployments, the number of replicas is set to 1. We're working on enabling replication in the cloud.

### Vector search configuration

Here are the parameters for each `VectorDB` type:

#### InMemoryExactNNVectorDB

This database performs exhaustive search on embeddings and has limited configuration settings:

- `workspace`: The folder where required data is persisted.

```python
InMemoryExactNNVectorDB[MyDoc](workspace='./vectordb')
InMemoryExactNNVectorDB[MyDoc].serve(workspace='./vectordb')
```

#### HNSWVectorDB

This database employs the HNSW (Hierarchical Navigable Small World) algorithm from [HNSWLib](https://github.com/nmslib/hnswlib) for Approximate Nearest Neighbor search. It provides several configuration options:

- `workspace`: Specifies the directory where required data is stored and persisted.

Additionally, HNSWVectorDB offers a set of configurations that allow tuning the performance and accuracy of the Nearest Neighbor search algorithm. Detailed descriptions of these configurations can be found in the [HNSWLib README](https://github.com/nmslib/hnswlib):

- `space`: Specifies the similarity metric used for the space (options are "l2", "ip", or "cosine"). The default is "l2".
- `max_elements`: Sets the initial capacity of the index, which can be increased dynamically. The default is 1024.
- `ef_construction`: This parameter controls the speed/accuracy trade-off during index construction. The default is 200.
- `ef`: This parameter controls the query time/accuracy trade-off. The default is 10.
- `M`: This parameter defines the maximum number of outgoing connections in the graph. The default is 16.
- `allow_replace_deleted`: If set to `True`, this allows replacement of deleted elements with newly added ones. The default is `False`.
- `num_threads`: This sets the default number of threads to be used during `index` and `search` operations. The default is 1.



### Command line interface

`vectordb` includes a simple CLI for serving and deploying your database:

| Description                     | Command | 
|---------------------------------| ---: |
| Serve your DB locally           | `vectordb serve --db example:db` |
| Deploy your DB on Jina AI Cloud |`vectordb deploy --db example:db` |



## Features

- **User-friendly Interface:** With `vectordb`, simplicity is key. Its intuitive interface is designed to accommodate users across varying levels of expertise.

- **Minimalistic Design:** `vectordb` packs all the essentials, with no unnecessary complexity. It ensures a seamless transition from local to server and cloud deployment.

- **Full CRUD Support:** From indexing and searching to updating and deleting, `vectordb` covers the entire spectrum of CRUD operations.

- **DB as a Service:** Harness the power of gRPC, HTTP, and Websocket protocols with `vectordb`. It enables you to serve your databases and conduct insertion or searching operations efficiently.

- **Scalability:** Experience the raw power of `vectordb`'s deployment capabilities, including robust scalability features like sharding and replication. Improve your service latency with sharding, while replication enhances availability and throughput.

- **Cloud Deployment:** Deploying your service in the cloud is a breeze with [Jina AI Cloud](https://cloud.jina.ai/). More deployment options are coming soon!

- **Serverless Capability:** `vectordb` can be deployed in a serverless mode in the cloud, ensuring optimal resource utilization and data availability as per your needs.

- **Multiple ANN Algorithms:** `vectordb` offers diverse implementations of Approximate Nearest Neighbors (ANN) algorithms. Here are the current offerings, with more integrations on the horizon:
   - InMemoryExactNNVectorDB (Exact NN Search): Implements Simple Nearest Neighbor Algorithm.
   - HNSWVectorDB (based on HNSW): Utilizes [HNSWLib](https://github.com/nmslib/hnswlib)


<!--(THIS CAN BE SHOWN WHEN FILTER IS ENABLED)- Filter capacity: `vectordb` allows you to have filters on top of the ANN search. -->

<!--(THIS CAN BE SHOWN WHEN FILTER IS ENABLED)- Customizable: `vectordb` can be easily extended to suit your specific needs or schemas, so you can build the database you want and for any input and output schema you want with the help of [DocArray](https://github.com/docarray/docarray).-->

## Roadmap

The future of Vector Database looks bright, and we have ambitious plans! Here's a sneak peek into the features we're currently developing:

- More ANN Search Algorithms: Our goal is to support an even wider range of ANN search algorithms.
- Enhanced Filtering Capabilities: We're working on enhancing our ANN Search solutions to support advanced filtering.
- Customizability: We aim to make `vectordb` highly customizable, allowing Python developers to tailor its behavior to their specific needs with ease.
- Expanding Serverless Capacity: We're striving to enhance the serverless capacity of `vectordb` in the cloud. While we currently support scaling between 0 and 1 replica, our goal is to extend this to 0 to N replicas.
- Expanded Deployment Options: We're actively working on facilitating the deployment of `vectordb` across various cloud platforms, with a broad range of options.

Need help with `vectordb`? Interested in using it but require certain features to meet your unique needs? Don't hesitate to reach out to us. Join our [Discord community](https://discord.jina.ai) to chat with us and other community members.

## Contributing

The VectorDB project is backed by [Jina AI](https://jina.ai) and licensed under Apache-2.0. Contributions from the community are greatly appreciated! If you have an idea for a new feature or an improvement, we would love to hear from you. We're always looking for ways to make `vectordb` more user-friendly and effective.


