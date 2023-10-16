import pytest
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import GraphTraversalSource


@pytest.fixture(scope="session")
def g() -> GraphTraversalSource:
    url = "ws://localhost:8182/gremlin"
    remoteConn = DriverRemoteConnection(url, "g")

    g = traversal().with_remote(remoteConn)
    yield g
    remoteConn.close()


@pytest.fixture(scope="function")
def reset(g) -> None:
    g.V().drop().iterate()
