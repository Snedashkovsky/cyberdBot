from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from config import GRAPHQL_HOST


async def execute_graphql(gql_query: str, url: str = GRAPHQL_HOST):
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url=url)
    # Create a GraphQL client using the defined transport
    async with Client(
        transport=transport, fetch_schema_from_transport=True,
    ) as session:
        # Execute single query
        query = gql(gql_query)
        return await session.execute(query)
